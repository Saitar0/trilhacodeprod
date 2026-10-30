import { useMemo, useState } from "react";
import type { ChangeEvent, ReactNode } from "react";
import { isTypedActivitiesEnabled } from "@/lib/typedActivityFeature";
import {
  ActivityValidationError,
  parsePublicTypedActivity,
  type PublicDiscursiveActivity,
  type PublicMatchingActivity,
  type PublicMultipleChoiceActivity,
  type PublicOrderingActivity,
  type PublicReviewActivity,
  type PublicShortAnswerActivity,
  type PublicTypedActivity,
} from "./types";

export type TypedActivityMode = "interactive" | "read_only" | "unavailable" | "error";

export interface TypedActivityRendererProps {
  activity: unknown;
  mode?: TypedActivityMode;
  message?: string;
}

const sectionClass =
  "w-full min-w-0 space-y-4 rounded-xl border border-slate-800 bg-slate-900/50 p-4 text-slate-200 sm:p-6";
const fieldClass =
  "w-full min-w-0 rounded-md border border-slate-700 bg-slate-950/60 px-3 py-2 text-sm text-slate-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-400 disabled:cursor-not-allowed disabled:opacity-60";
const itemClass =
  "min-w-0 rounded-lg border border-slate-800 bg-slate-950/40 px-3 py-3 text-sm";

function ActivityHeader({ activity }: { activity: PublicTypedActivity }) {
  const titleId = "typed-title-" + activity.activity_ref;
  return (
    <>
      <header className="space-y-2">
        <h2 id={titleId} className="break-words text-base font-semibold text-slate-100">
          {activity.title}
        </h2>
        <p className="break-words text-sm leading-6 text-slate-200">{activity.prompt}</p>
        {activity.instructions && (
          <p className="break-words text-sm text-slate-400">{activity.instructions}</p>
        )}
      </header>
      {activity.references && activity.references.length > 0 && (
        <ul aria-label="Referências da atividade" className="space-y-1 text-xs text-slate-400">
          {activity.references.map((reference, index) => (
            <li key={index} className="break-words">
              {reference.label}
              {reference.raw_text ? " — " + reference.raw_text : ""}
              {reference.url ? " — " + reference.url : ""}
              {reference.target_ref ? " — " + reference.target_ref : ""}
            </li>
          ))}
        </ul>
      )}
    </>
  );
}

type InteractionState = "initial" | "editing" | "invalid" | "ready";

function ModeNotice({
  mode,
  message,
  state = "initial",
}: {
  mode: TypedActivityMode;
  message?: string;
  state?: InteractionState;
}) {
  if (mode === "interactive") {
    const stateText: Record<InteractionState, string> = {
      initial: "Atividade pronta para começar. O envio não está disponível nesta etapa.",
      editing: "Resposta em edição. O envio não está disponível nesta etapa.",
      invalid: "Entrada inválida. Revise o campo indicado.",
      ready: "Pronto para envio, mas o envio não está disponível nesta demonstração.",
    };
    return <p role="status" className="text-xs text-slate-400">{stateText[state]}</p>;
  }
  if (mode === "error") {
    return (
      <p role="alert" className="rounded-md border border-rose-500/40 bg-rose-500/10 p-3 text-sm text-rose-200">
        {message || "Não foi possível apresentar esta atividade."}
      </p>
    );
  }
  if (mode === "unavailable") {
    return (
      <p role="status" className="rounded-md border border-amber-500/40 bg-amber-500/10 p-3 text-sm text-amber-100">
        {message || "Esta atividade está indisponível nesta demonstração."}
      </p>
    );
  }
  return <p role="status" className="text-xs text-slate-400">Somente leitura.</p>;
}

function ActivityFrame({
  activity,
  mode,
  message,
  children,
  state,
}: {
  activity: PublicTypedActivity;
  mode: TypedActivityMode;
  message?: string;
  children: ReactNode;
  state?: InteractionState;
}) {
  return (
    <section aria-labelledby={"typed-title-" + activity.activity_ref} className={sectionClass}>
      <ActivityHeader activity={activity} />
      {children}
      <ModeNotice mode={mode} message={message} state={state} />
    </section>
  );
}

function MultipleChoiceActivity({ activity, mode, message }: {
  activity: PublicMultipleChoiceActivity;
  mode: TypedActivityMode;
  message?: string;
}) {
  const [selected, setSelected] = useState<string | null>(null);
  const disabled = mode !== "interactive";
  return (
    <ActivityFrame activity={activity} mode={mode} message={message} state={selected ? "ready" : "initial"}>
      <fieldset disabled={disabled} className="min-w-0 space-y-2">
        <legend className="mb-2 text-sm font-medium text-slate-100">Alternativas</legend>
        {activity.options.map((option, index) => {
          const inputId = "typed-" + activity.activity_ref + "-option-" + index;
          return (
            <label key={option.option_id} htmlFor={inputId} className={itemClass + " flex cursor-pointer items-start gap-3 hover:border-slate-600"}>
              <input
                id={inputId}
                name={"typed-" + activity.activity_ref}
                type="radio"
                value={option.option_id}
                checked={selected === option.option_id}
                onChange={() => setSelected(option.option_id)}
                className="mt-1 h-4 w-4 shrink-0 accent-cyan-400 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-400"
              />
              <span className="break-words">{option.text}</span>
            </label>
          );
        })}
      </fieldset>
      {selected && <p role="status" className="text-sm text-slate-300">Alternativa selecionada. Nenhuma correção foi realizada.</p>}
    </ActivityFrame>
  );
}

const SHORT_ANSWER_LIMIT = 2_000;
const DISCURSIVE_ANSWER_LIMIT = 10_000;

function TextResponse({
  activity,
  mode,
  message,
  longForm,
}: {
  activity: PublicShortAnswerActivity | PublicDiscursiveActivity;
  mode: TypedActivityMode;
  message?: string;
  longForm: boolean;
}) {
  const [value, setValue] = useState("");
  const [touched, setTouched] = useState(false);
  const maxLength = longForm ? DISCURSIVE_ANSWER_LIMIT : SHORT_ANSWER_LIMIT;
  const invalid = touched && value.trim().length === 0;
  const interactionState: InteractionState = invalid ? "invalid" : value.trim() ? "ready" : "initial";
  const disabled = mode !== "interactive";
  const inputId = "typed-" + activity.activity_ref + "-response";
  const helpId = inputId + "-help";
  const label = longForm ? "Sua resposta discursiva" : "Sua resposta curta";
  const onChange = (event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setValue(event.target.value);
    setTouched(true);
  };

  return (
    <ActivityFrame activity={activity} mode={mode} message={message} state={interactionState}>
      <div className="min-w-0 space-y-2">
        <label htmlFor={inputId} className="block text-sm font-medium text-slate-100">{label}</label>
        {longForm ? (
          <textarea
            id={inputId}
            value={value}
            maxLength={maxLength}
            disabled={disabled}
            required
            aria-invalid={invalid}
            aria-describedby={helpId}
            onChange={onChange}
            onBlur={() => setTouched(true)}
            rows={7}
            className={fieldClass}
          />
        ) : (
          <input
            id={inputId}
            value={value}
            maxLength={maxLength}
            disabled={disabled}
            required
            aria-invalid={invalid}
            aria-describedby={helpId}
            onChange={onChange}
            onBlur={() => setTouched(true)}
            type="text"
            autoComplete="off"
            className={fieldClass}
          />
        )}
        <div id={helpId} className="flex flex-wrap justify-between gap-2 text-xs">
          <span role={invalid ? "alert" : undefined} className={invalid ? "text-rose-300" : "text-slate-400"}>
            {invalid ? "Informe uma resposta antes de continuar." : "A resposta não será avaliada nesta demonstração."}
          </span>
          <span aria-label={value.length + " de " + maxLength + " caracteres"} className="text-slate-500">
            {value.length}/{maxLength}
          </span>
        </div>
      </div>
    </ActivityFrame>
  );
}

function ShortAnswerActivity({ activity, mode, message }: {
  activity: PublicShortAnswerActivity;
  mode: TypedActivityMode;
  message?: string;
}) {
  return <TextResponse activity={activity} mode={mode} message={message} longForm={false} />;
}

function DiscursiveActivity({ activity, mode, message }: {
  activity: PublicDiscursiveActivity;
  mode: TypedActivityMode;
  message?: string;
}) {
  return <TextResponse activity={activity} mode={mode} message={message} longForm />;
}

function MatchingActivity({ activity, mode, message }: {
  activity: PublicMatchingActivity;
  mode: TypedActivityMode;
  message?: string;
}) {
  const [matches, setMatches] = useState<Record<string, string>>({});
  const disabled = mode !== "interactive";
  const canPresent = activity.left_items.length > 0 && activity.right_items.length > 0;
  const matchedCount = Object.keys(matches).length;
  const interactionState: InteractionState = matchedCount === 0 ? "initial" : matchedCount >= activity.left_items.length ? "ready" : "editing";
  return (
    <ActivityFrame activity={activity} mode={mode} message={message} state={interactionState}>
      {!canPresent ? (
        <p role="status" className="text-sm text-slate-400">
          A fonte não fornece os dois lados estruturados para esta atividade.
        </p>
      ) : (
        <div className="grid min-w-0 gap-3 md:grid-cols-2">
          {activity.left_items.map((item, index) => {
            const selectId = "typed-" + activity.activity_ref + "-match-" + index;
            return (
              <div key={item.ref} className={itemClass + " space-y-2"}>
                <label htmlFor={selectId} className="block break-words font-medium text-slate-100">{item.text}</label>
                <select
                  id={selectId}
                  value={matches[item.ref] ?? ""}
                  disabled={disabled}
                  onChange={(event) => setMatches((current) => ({ ...current, [item.ref]: event.target.value }))}
                  className={fieldClass}
                >
                  <option value="">Selecione uma associação</option>
                  {activity.right_items.map((right) => (
                    <option key={right.ref} value={right.ref}>{right.text}</option>
                  ))}
                </select>
              </div>
            );
          })}
        </div>
      )}
      {Object.keys(matches).length > 0 && <p role="status" className="text-sm text-slate-300">Associações selecionadas. Nenhuma correção foi realizada.</p>}
    </ActivityFrame>
  );
}

function OrderingActivity({ activity, mode, message }: {
  activity: PublicOrderingActivity;
  mode: TypedActivityMode;
  message?: string;
}) {
  const [items, setItems] = useState(activity.items);
  const disabled = mode !== "interactive";
  const orderChanged = activity.items.some((item, index) => items[index]?.ref !== item.ref);

  function move(index: number, delta: number) {
    setItems((current) => {
      const nextIndex = index + delta;
      if (nextIndex < 0 || nextIndex >= current.length) return current;
      const next = [...current];
      [next[index], next[nextIndex]] = [next[nextIndex], next[index]];
      return next;
    });
  }

  return (
    <ActivityFrame activity={activity} mode={mode} message={message} state={orderChanged ? "ready" : "initial"}>
      {items.length === 0 ? (
        <p role="status" className="text-sm text-slate-400">A fonte não fornece itens de ordenação estruturados.</p>
      ) : (
        <ol aria-label="Itens em ordenação" className="min-w-0 space-y-2">
          {items.map((item, index) => (
            <li key={item.ref} className={itemClass + " flex min-w-0 items-center gap-3"}>
              <span className="min-w-0 flex-1 break-words">{item.text}</span>
              <div className="flex shrink-0 gap-1">
                <button
                  type="button"
                  aria-label={"Mover " + item.text + " para cima"}
                  onClick={() => move(index, -1)}
                  disabled={disabled || index === 0}
                  className="rounded border border-slate-700 px-2 py-1 text-xs focus-visible:outline focus-visible:outline-2 focus-visible:outline-cyan-400 disabled:opacity-40"
                >Subir</button>
                <button
                  type="button"
                  aria-label={"Mover " + item.text + " para baixo"}
                  onClick={() => move(index, 1)}
                  disabled={disabled || index === items.length - 1}
                  className="rounded border border-slate-700 px-2 py-1 text-xs focus-visible:outline focus-visible:outline-2 focus-visible:outline-cyan-400 disabled:opacity-40"
                >Descer</button>
              </div>
            </li>
          ))}
        </ol>
      )}
      {items.length > 0 && <p role="status" className="text-sm text-slate-300">A ordem pode ser ajustada localmente; não há pontuação.</p>}
    </ActivityFrame>
  );
}

function ReviewActivity({ activity, mode, message }: {
  activity: PublicReviewActivity;
  mode: TypedActivityMode;
  message?: string;
}) {
  return (
    <ActivityFrame activity={activity} mode={mode} message={message}>
      <p className="rounded-md border border-cyan-500/30 bg-cyan-500/5 p-3 text-sm text-cyan-100">
        Revisão formativa · sem pontuação.
      </p>
    </ActivityFrame>
  );
}

function renderActivity(
  activity: PublicTypedActivity,
  mode: TypedActivityMode,
  message?: string,
) {
  switch (activity.type) {
    case "multiple_choice":
      return <MultipleChoiceActivity key={activity.activity_ref + ":" + activity.version_ref} activity={activity} mode={mode} message={message} />;
    case "short_answer":
      return <ShortAnswerActivity key={activity.activity_ref + ":" + activity.version_ref} activity={activity} mode={mode} message={message} />;
    case "discursive":
      return <DiscursiveActivity key={activity.activity_ref + ":" + activity.version_ref} activity={activity} mode={mode} message={message} />;
    case "matching":
      return <MatchingActivity key={activity.activity_ref + ":" + activity.version_ref} activity={activity} mode={mode} message={message} />;
    case "ordering":
      return <OrderingActivity key={activity.activity_ref + ":" + activity.version_ref} activity={activity} mode={mode} message={message} />;
    case "review":
      return <ReviewActivity key={activity.activity_ref + ":" + activity.version_ref} activity={activity} mode={mode} message={message} />;
  }
}

export function TypedActivityRenderer({
  activity,
  mode = "interactive",
  message,
}: TypedActivityRendererProps) {
  const parsed = useMemo(() => {
    try {
      return { activity: parsePublicTypedActivity(activity), error: null };
    } catch (error) {
      return {
        activity: null,
        error: error instanceof ActivityValidationError
          ? error.message
          : "A atividade possui um formato inválido.",
      };
    }
  }, [activity]);

  if (!isTypedActivitiesEnabled()) {
    return (
      <p role="status" className={sectionClass}>
        Atividades tipadas desativadas. O conteúdo curricular existente continua disponível.
      </p>
    );
  }

  if (!parsed.activity) {
    return (
      <p role="alert" className={sectionClass}>
        Não foi possível validar esta atividade: {parsed.error}
      </p>
    );
  }

  return renderActivity(parsed.activity, mode, message);
}