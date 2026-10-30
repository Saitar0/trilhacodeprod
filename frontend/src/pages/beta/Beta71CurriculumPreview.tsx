import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import { api, apiError } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { Markdown } from "@/components/common/Markdown";

type UnitRef = { id: string; title: string; order: number };
type ModuleRef = { id: string; title: string; order: number; units: UnitRef[] };
type PhaseTree = { id: string; title: string; modules: ModuleRef[] };
type Option = { id: string; label: string };
type Question = { id: string; order: number; version: string; prompt: string; options: Option[] };
type Exercise = { id: string; order: number; title: string; prompt: string; version: string };
type Unit = {
  id: string; title: string; module_id: string; objective: string; version: string;
  topics: { id: string; title: string; order: number; segments: { id: string; title: string; order: number; body: string }[] }[];
  summary: string; references: { id: string; order: number; title: string; description: string; url: string | null }[];
  quizzes: Question[]; exercises: Exercise[]; criterion: { source_text: string | null; state: string };
};
type Progress = {
  units: { unit_id: string; quizzes_answered: number; quizzes_total: number; exercises_submitted: number; exercises_total: number; awaiting_review: number; revision_required: number; project_state: string; project_approved: number; criterion_state: string; unit_completion: string; mastery: string }[];
  modules: { module_id: string; units: number; quizzes_answered: number; quizzes_total: number; exercises_submitted: number; exercises_total: number; awaiting_review: number; revision_required: number; project_approved: number; completion: string }[];
  phase: { units: number; completion: string; mastery: string; project_3_5_required_review: boolean };
};
type Project = { id: string; title: string; version: string; completion: string; artifacts: { id: string; kind: string; order: number; title: string; visibility: string; content: string | null }[] };
type Submission = { id: string; unit_id: string; activity_id: string; state: string; feedback: string | null; review_revision: number; attempt: number; previous_submission_id?: string | null };
type ProjectQueueItem = { id: string; unit_id: string; project_id: string; answer: string; state: string; revision: number; source_sha256: string };
type ReviewerRubric = { rubric_id: string; version: string; state: string; criteria: { criterion_id: string; description: string; required: boolean | null }[] };
type AssessmentHistory = { assessment_id: string; submission_id: string; outcome: string; feedback: string; resulting_state: string; decided_at: string };

const batchId = import.meta.env.VITE_BETA7_1_PREVIEW_BATCH_ID as string;

function operationKey(): string {
  return crypto.randomUUID();
}

export default function Beta71CurriculumPreview() {
  const { user, login, logout } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [tree, setTree] = useState<PhaseTree | null>(null);
  const [unit, setUnit] = useState<Unit | null>(null);
  const [progress, setProgress] = useState<Progress | null>(null);
  const [project, setProject] = useState<Project | null>(null);
  const [submissions, setSubmissions] = useState<Submission[]>([]);
  const [queue, setQueue] = useState<ProjectQueueItem[]>([]);
  const [reviewerRubric, setReviewerRubric] = useState<ReviewerRubric | null>(null);
  const [assessmentHistory, setAssessmentHistory] = useState<AssessmentHistory[]>([]);
  const [selected, setSelected] = useState<Record<string, string>>({});
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [delivery, setDelivery] = useState("");
  const [loading, setLoading] = useState(false);

  const allUnits = useMemo(() => tree?.modules.flatMap((module) => module.units) ?? [], [tree]);

  const refreshProgress = useCallback(async () => {
    const [progressResponse, submissionsResponse, historyResponse] = await Promise.all([
      api.get<Progress>(`/beta7-1/preview/batches/${batchId}/progress`),
      api.get<{ exercises: Submission[]; projects: Submission[] }>(`/beta7-1/preview/batches/${batchId}/submissions/mine`),
      api.get<AssessmentHistory[]>(`/beta7-2/assessment/batches/${batchId}/project/assessment-history/mine`),
    ]);
    setProgress(progressResponse.data);
    setSubmissions([...submissionsResponse.data.exercises, ...submissionsResponse.data.projects]);
    setAssessmentHistory(historyResponse.data);
  }, []);

  const loadUnit = useCallback(async (unitId: string) => {
    setError("");
    try {
      const response = await api.get<Unit>(`/beta7-1/preview/batches/${batchId}/units/${encodeURIComponent(unitId)}`);
      setUnit(response.data);
      setSelected({});
      if (unitId === "3.5") {
        const projectResponse = await api.get<Project>(`/beta7-1/preview/batches/${batchId}/project`);
        setProject(projectResponse.data);
      }
    } catch (cause) {
      setError(apiError(cause));
    }
  }, []);

  useEffect(() => {
    if (!user) return;
    let active = true;
    setLoading(true);
    Promise.all([
      api.get<PhaseTree>(`/beta7-1/preview/batches/${batchId}`),
      api.get<Progress>(`/beta7-1/preview/batches/${batchId}/progress`),
      api.get<{ exercises: Submission[]; projects: Submission[] }>(`/beta7-1/preview/batches/${batchId}/submissions/mine`),
      api.get<AssessmentHistory[]>(`/beta7-2/assessment/batches/${batchId}/project/assessment-history/mine`),
    ]).then(([treeResponse, progressResponse, submissionResponse, historyResponse]) => {
      if (!active) return;
      setTree(treeResponse.data);
      setProgress(progressResponse.data);
      setSubmissions([...submissionResponse.data.exercises, ...submissionResponse.data.projects]);
      setAssessmentHistory(historyResponse.data);
      const first = treeResponse.data.modules[0]?.units[0];
      if (first) void loadUnit(first.id);
      if (user.permissions.includes("submissions.grade")) {
        void Promise.all([
          api.get<ProjectQueueItem[]>(`/beta7-1/preview/batches/${batchId}/project/review-queue`),
          api.get<ReviewerRubric>(`/beta7-2/assessment/batches/${batchId}/project/rubric`),
        ])
          .then(([queueResponse, rubricResponse]) => {
            if (!active) return;
            setQueue(queueResponse.data);
            setReviewerRubric(rubricResponse.data);
          })
          .catch(() => active && setQueue([]));
      }
    }).catch((cause: unknown) => {
      if (active) setError(apiError(cause));
    }).finally(() => active && setLoading(false));
    return () => { active = false; };
  }, [user, loadUnit]);

  const doLogin = async (event: FormEvent) => {
    event.preventDefault();
    setError("");
    try {
      await login(email, password);
    } catch (cause) {
      setError(apiError(cause));
    }
  };

  const submitQuiz = async (question: Question) => {
    if (!unit || !selected[question.id]) return;
    setError("");
    try {
      await api.post(`/beta7-1/preview/batches/${batchId}/units/${unit.id}/quizzes/${question.id}/attempts`, {
        selected_option_id: selected[question.id], source_sha256: question.version,
      }, { headers: { "Idempotency-Key": operationKey() } });
      await refreshProgress();
    } catch (cause) {
      setError(apiError(cause));
    }
  };

  const submitExercise = async (exercise: Exercise) => {
    if (!unit || !answers[exercise.id]?.trim()) return;
    setError("");
    try {
      await api.post(`/beta7-1/preview/batches/${batchId}/units/${unit.id}/exercises/${exercise.id}/submissions`, {
        answer_text: answers[exercise.id], source_sha256: exercise.version,
        unit_source_sha256: unit.version,
      }, { headers: { "Idempotency-Key": operationKey() } });
      await refreshProgress();
    } catch (cause) {
      setError(apiError(cause));
    }
  };

  const submitDelivery = async () => {
    if (!project || !delivery.trim()) return;
    setError("");
    try {
      await api.post(`/beta7-1/preview/batches/${batchId}/project/submissions`, {
        delivery_text: delivery, source_sha256: project.version,
      }, { headers: { "Idempotency-Key": operationKey() } });
      setDelivery("");
      await refreshProgress();
    } catch (cause) {
      setError(apiError(cause));
    }
  };

  const reviewProject = async (item: ProjectQueueItem) => {
    if (!reviewerRubric) return;
    setError("");
    try {
      await api.post(`/beta7-2/assessment/batches/${batchId}/project/submissions/${item.id}/assess`, {
        project_version: item.source_sha256,
        rubric_id: reviewerRubric.rubric_id,
        rubric_version: reviewerRubric.version,
        expected_revision: item.revision,
        outcome: "NEEDS_REVISION",
        feedback: "Entrega recebida para revisão. A aprovação do projeto permanece bloqueada até decisão pedagógica sobre a rubrica.",
      }, { headers: { "Idempotency-Key": operationKey() } });
      const response = await api.get<ProjectQueueItem[]>(`/beta7-1/preview/batches/${batchId}/project/review-queue`);
      setQueue(response.data);
    } catch (cause) {
      setError(apiError(cause));
    }
  };

  if (user === null) {
    return (
      <main className="mx-auto max-w-xl p-6" role="status" data-testid="beta71-preview-auth-check">
        Verificando sessão…
      </main>
    );
  }

  if (user === false) {
    return (
      <main className="mx-auto max-w-xl p-6" data-testid="beta71-preview-login">
        <h1 className="text-2xl font-bold">Prévia curricular Beta 7.1</h1>
        <p className="my-3 text-sm text-slate-400">Ambiente isolado para identidades sintéticas autorizadas.</p>
        <form className="space-y-3" onSubmit={doLogin}>
          <label className="block">E-mail<input className="mt-1 block w-full rounded border p-2 text-slate-900" type="email" value={email} onChange={(event) => setEmail(event.target.value)} required data-testid="preview-email" /></label>
          <label className="block">Senha<input className="mt-1 block w-full rounded border p-2 text-slate-900" type="password" value={password} onChange={(event) => setPassword(event.target.value)} required data-testid="preview-password" /></label>
          <button className="rounded bg-emerald-600 px-4 py-2 text-white" type="submit" data-testid="preview-login-submit">Entrar na prévia</button>
        </form>
        {error && <p role="alert" className="mt-3 text-rose-400">{error}</p>}
      </main>
    );
  }

  return (
    <main className="mx-auto grid max-w-7xl gap-6 p-4 lg:grid-cols-[280px_minmax(0,1fr)]" data-testid="beta71-preview">
      <aside className="rounded-lg border border-slate-700 p-4">
        <div className="flex items-start justify-between gap-2">
          <div><p className="text-xs uppercase tracking-wider text-emerald-400">prévia isolada</p><h1 className="mt-1 text-xl font-bold">Fase 1 revisada</h1></div>
          <button type="button" className="text-sm text-slate-300 underline" onClick={() => void logout()}>Sair</button>
        </div>
        <p className="my-3 text-sm text-slate-400">{user.email}</p>
        {tree?.modules.map((module) => (
          <section key={module.id} className="mb-4" data-testid={`preview-module-${module.id}`}>
            <h2 className="mb-2 font-semibold">Módulo {module.id}</h2>
            <nav className="space-y-1" aria-label={`Unidades do módulo ${module.id}`}>
              {module.units.map((item) => (
                <button key={item.id} type="button" onClick={() => void loadUnit(item.id)}
                  aria-current={unit?.id === item.id ? "page" : undefined}
                  data-testid={`preview-unit-${item.id}`}
                  className={`block w-full rounded px-2 py-2 text-left text-sm ${unit?.id === item.id ? "bg-emerald-900/50 text-emerald-100" : "text-slate-300 hover:bg-slate-800"}`}>
                  {item.title}
                </button>
              ))}
            </nav>
            {progress && <p className="mt-2 text-xs text-slate-400" data-testid={`preview-module-progress-${module.id}`}>
              {progress.modules.find((row) => row.module_id === module.id)?.quizzes_answered ?? 0} / {progress.modules.find((row) => row.module_id === module.id)?.quizzes_total ?? 0} questões · conclusão não avaliada
            </p>}
          </section>
        ))}
        <div className="border-t border-slate-700 pt-3" data-testid="preview-phase-progress">
          <h2 className="font-semibold">Progresso da fase</h2>
          <p className="mt-1 text-sm">{progress?.phase.completion ?? "Carregando…"}</p>
          <p className="text-xs text-slate-400">Domínio: {progress?.phase.mastery ?? "não avaliado"}</p>
        </div>
      </aside>

      <section className="min-w-0 rounded-lg border border-slate-700 p-4 md:p-6">
        {loading && <p role="status">Carregando prévia…</p>}
        {error && <p role="alert" className="mb-4 rounded border border-rose-800 p-3 text-rose-300">{error}</p>}
        {unit && <>
          <header className="mb-6 border-b border-slate-700 pb-4">
            <p className="text-sm text-emerald-400">Módulo {unit.module_id} · Unidade {unit.id}</p>
            <h2 className="mt-1 text-3xl font-bold" data-testid="preview-unit-title">{unit.title}</h2>
            <p className="mt-3 text-slate-300">{unit.objective}</p>
          </header>
          <div className="flex justify-between gap-2">
            <button type="button" data-testid="preview-previous-unit" disabled={!allUnits.find((item) => item.id === unit.id) || allUnits[0]?.id === unit.id}
              onClick={() => { const index = allUnits.findIndex((item) => item.id === unit.id); if (index > 0) void loadUnit(allUnits[index - 1].id); }}>Unidade anterior</button>
            <button type="button" data-testid="preview-next-unit" disabled={allUnits.at(-1)?.id === unit.id}
              onClick={() => { const index = allUnits.findIndex((item) => item.id === unit.id); if (index >= 0 && index < allUnits.length - 1) void loadUnit(allUnits[index + 1].id); }}>Próxima unidade</button>
          </div>

          <div className="mt-6 space-y-8">
            {unit.topics.map((topic) => <article key={topic.id} className="border-l-2 border-emerald-700 pl-4" data-testid={`preview-topic-${topic.id}`}>
              <h3 className="text-xl font-semibold">{topic.title}</h3>
              {topic.segments.map((segment) => <section key={segment.id} className="mt-4" data-testid={`preview-segment-${segment.id}`}>
                <h4 className="font-medium text-slate-200">{segment.title}</h4>
                <Markdown className="mt-2 text-slate-300">{segment.body}</Markdown>
              </section>)}
            </article>)}
          </div>

          {unit.summary && <section className="mt-8 rounded-lg bg-slate-800/60 p-4" data-testid="preview-summary"><h3 className="text-lg font-semibold">Resumo</h3><Markdown className="mt-2 text-slate-300">{unit.summary}</Markdown></section>}
          {!!unit.references.length && <section className="mt-8" data-testid="preview-references"><h3 className="text-lg font-semibold">Referências</h3><ul className="mt-2 list-disc space-y-2 pl-5">{unit.references.map((reference) => <li key={reference.id}><strong>{reference.title}</strong>{reference.description && <span> — {reference.description}</span>}{reference.url && <> <a className="underline" href={reference.url} target="_blank" rel="noreferrer">Abrir referência</a></>}</li>)}</ul></section>}

          {!!unit.quizzes.length && <section className="mt-10" data-testid="preview-quizzes"><h3 className="mb-4 text-2xl font-bold">Quiz</h3><div className="space-y-5">{unit.quizzes.map((question) => <fieldset key={question.id} className="rounded-lg border border-slate-700 p-4" data-testid={`preview-question-${question.id}`}>
            <legend className="px-2 font-semibold">{question.order}. {question.prompt}</legend>
            {question.options.map((option) => <label key={option.id} className="mt-2 flex cursor-pointer items-start gap-2"><input type="radio" name={question.id} value={option.id} checked={selected[question.id] === option.id} onChange={() => setSelected((current) => ({ ...current, [question.id]: option.id }))} />{option.label}</label>)}
            <button type="button" className="mt-3 rounded bg-emerald-700 px-3 py-1" data-testid={`preview-quiz-submit-${question.id}`} disabled={!selected[question.id]} onClick={() => void submitQuiz(question)}>Enviar resposta</button>
          </fieldset>)}</div></section>}

          {!!unit.exercises.length && <section className="mt-10" data-testid="preview-exercises"><h3 className="mb-4 text-2xl font-bold">Exercícios</h3><div className="space-y-4">{unit.exercises.map((exercise) => {
            const own = submissions.find((item) => item.activity_id === exercise.id);
            return <article key={exercise.id} className="rounded-lg border border-slate-700 p-4" data-testid={`preview-exercise-${exercise.id}`}>
              <h4 className="font-semibold">{exercise.title}</h4><Markdown className="mt-2 text-slate-300">{exercise.prompt}</Markdown>
              <label className="mt-3 block text-sm">Sua resposta<textarea className="mt-1 block min-h-28 w-full rounded border p-2 text-slate-900" value={answers[exercise.id] ?? ""} onChange={(event) => setAnswers((current) => ({ ...current, [exercise.id]: event.target.value }))} data-testid={`preview-exercise-answer-${exercise.id}`} /></label>
              <button className="mt-2 rounded bg-emerald-700 px-3 py-1" type="button" data-testid={`preview-exercise-submit-${exercise.id}`} disabled={!answers[exercise.id]?.trim()} onClick={() => void submitExercise(exercise)}>Enviar para correção</button>
              {own && <p className="mt-2 text-sm" data-testid={`preview-exercise-state-${exercise.id}`}>{own.state}{own.feedback && <span> — {own.feedback}</span>}</p>}
            </article>;
          })}</div></section>}

          <section className="mt-8 rounded-lg border border-amber-700/60 p-4" data-testid="preview-completion-criterion">
            <h3 className="font-semibold">Critério de conclusão</h3>
            <p className="mt-1 text-sm">{unit.criterion.source_text ?? "A fonte não declara um critério para esta unidade."}</p>
            <p className="mt-2 text-xs text-amber-300">{unit.criterion.state}; leitura e envio não são tratados como domínio.</p>
          </section>
          {progress && <section className="mt-6 rounded-lg bg-slate-800/60 p-4" data-testid={`preview-progress-${unit.id}`}>
            <h3 className="font-semibold">Progresso desta unidade</h3>
            <p>{progress.units.find((item) => item.unit_id === unit.id)?.quizzes_answered ?? 0} / {progress.units.find((item) => item.unit_id === unit.id)?.quizzes_total ?? 0} questões respondidas</p>
            <p>{progress.units.find((item) => item.unit_id === unit.id)?.exercises_submitted ?? 0} / {progress.units.find((item) => item.unit_id === unit.id)?.exercises_total ?? 0} exercícios enviados</p>
            <p>{progress.units.find((item) => item.unit_id === unit.id)?.unit_completion}; domínio: {progress.units.find((item) => item.unit_id === unit.id)?.mastery}</p>
          </section>}
        </>}

        {unit?.id === "3.5" && project && <section className="mt-10 border-t border-slate-700 pt-6" data-testid="preview-project">
          <h3 className="text-2xl font-bold">Projeto incremental da fase</h3>
          <p className="mt-1 text-sm text-amber-300">Conclusão: {project.completion}</p>
          <div className="mt-4 space-y-3">{project.artifacts.map((artifact) => <article key={artifact.id} className="rounded border border-slate-700 p-3" data-testid={`project-artifact-${artifact.id}`}>
            <h4 className="font-semibold">{artifact.title}</h4><p className="text-xs text-slate-400">{artifact.kind} · {artifact.visibility}</p>{artifact.content && <Markdown className="mt-2">{artifact.content}</Markdown>}
          </article>)}</div>
          <label className="mt-5 block">Entrega textual<textarea className="mt-1 block min-h-32 w-full rounded border p-2 text-slate-900" value={delivery} onChange={(event) => setDelivery(event.target.value)} data-testid="preview-project-delivery" /></label>
          <button className="mt-2 rounded bg-emerald-700 px-3 py-1" type="button" disabled={!delivery.trim()} onClick={() => void submitDelivery()} data-testid="preview-project-submit">Enviar entrega</button>
          {submissions.filter((item) => item.unit_id === "3.5").map((item) => <p key={item.id} className="mt-2 text-sm" data-testid={`preview-project-submission-state-${item.id}`}>Tentativa {item.attempt}: {item.state}{item.previous_submission_id && " · vinculada à tentativa anterior"}{item.feedback && ` — ${item.feedback}`}</p>)}
          {user.permissions.includes("submissions.grade") && <div className="mt-6" data-testid="preview-review-queue">
            <h4 className="font-semibold">Entregas para avaliação</h4>
            {reviewerRubric && <div className="my-3 rounded border border-amber-700 p-3" data-testid="project-rubric-status">
              <p>Rubrica {reviewerRubric.version}: {reviewerRubric.state}</p>
              <p className="text-sm">Aprovação indisponível enquanto a decisão pedagógica estiver pendente.</p>
              <button type="button" disabled className="mt-2 cursor-not-allowed rounded bg-slate-700 px-3 py-1" data-testid="project-approve-disabled">Aprovar — bloqueado</button>
            </div>}
            {queue.map((item) => <article className="mt-3 rounded border border-slate-700 p-3" key={item.id} data-testid={`preview-review-item-${item.id}`}>
              <p>{item.answer}</p><p className="text-xs text-slate-400">{item.state} · revisão {item.revision}</p>
              <button className="mt-2 rounded bg-amber-700 px-3 py-1" onClick={() => void reviewProject(item)} type="button">Registrar feedback e solicitar revisão</button>
            </article>)}
          </div>}
          {assessmentHistory.filter((item) => submissions.some((submission) => submission.id === item.submission_id)).map((item) => <p key={item.assessment_id} className="mt-2 text-sm" data-testid={`project-assessment-${item.assessment_id}`}>{item.resulting_state} — {item.feedback}</p>)}
        </section>}
      </section>
    </main>
  );
}
