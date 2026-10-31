import { useCallback, useEffect, useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";
import { api } from "@/lib/api";
import { Review, StudyNote, Submission } from "@/types";

type NoteSaveState = "saved" | "pending" | "saving" | "error" | "conflict";
type NoteConflict = { current: StudyNote | null };
type NoteWriteResult = StudyNote | { deleted: true; version: number };
type NoteError = {
  response?: {
    status?: number;
    data?: { error?: { details?: { code?: string; current?: StudyNote | null } } };
  };
};

type NoteFlush = () => Promise<boolean>;
type NoteDraft = {
  identity: string;
  userId: string;
  nodeId: string;
  blockId: string | null;
  body: string;
  savedBody: string;
  version: number;
};
const pendingNoteFlushes = new Map<symbol, { identity: string; userId: string; flush: NoteFlush }>();
const pendingNoteDrafts = new Map<string, NoteDraft>();
const discardedNoteDrafts = new Set<string>();

function noteBody(result: NoteWriteResult): string {
  return "deleted" in result ? "" : result.body;
}

export function discardPendingNoteDrafts(userId?: string) {
  for (const [identity, draft] of pendingNoteDrafts) {
    if (!userId || draft.userId === userId) {
      discardedNoteDrafts.add(identity);
      pendingNoteDrafts.delete(identity);
    }
  }
}

export function discardPendingNoteDraftsExcept(userId: string) {
  for (const [identity, draft] of pendingNoteDrafts) {
    if (draft.userId !== userId) {
      discardedNoteDrafts.add(identity);
      pendingNoteDrafts.delete(identity);
    }
  }
}

async function flushOrphanNoteDraft(identity: string, draft: NoteDraft): Promise<boolean> {
  try {
    const response = await api.put<NoteWriteResult>("/notes", {
      node_id: draft.nodeId,
      block_id: draft.blockId,
      body: draft.body,
      expected_version: draft.version,
    });
    if (pendingNoteDrafts.get(identity) === draft) pendingNoteDrafts.delete(identity);
    return noteBody(response.data) === draft.body;
  } catch (error) {
    const current = (error as NoteError).response?.data?.error?.details?.current;
    const currentBody = current?.deleted ? "" : current?.body || "";
    if (currentBody === draft.body) {
      if (pendingNoteDrafts.get(identity) === draft) pendingNoteDrafts.delete(identity);
      return true;
    }
    return false;
  }
}

export async function flushPendingNoteSaves(userId?: string): Promise<boolean> {
  const active = [...pendingNoteFlushes.values()].filter((entry) => !userId || entry.userId === userId);
  const activeIdentities = new Set(active.map((entry) => entry.identity));
  const activeResults = await Promise.all(active.map((entry) => entry.flush().catch(() => false)));
  const orphanDrafts = [...pendingNoteDrafts.entries()].filter(([identity, draft]) =>
    !activeIdentities.has(identity) && (!userId || draft.userId === userId));
  const orphanResults = await Promise.all(orphanDrafts.map(([identity, draft]) => flushOrphanNoteDraft(identity, draft)));
  return [...activeResults, ...orphanResults].every(Boolean);
}

export async function navigateAfterNoteSave(
  navigate: (to: string) => void, to: string, userId?: string,
): Promise<boolean> {
  if (await flushPendingNoteSaves(userId)) {
    navigate(to);
    return true;
  }
  if (window.confirm("Há uma anotação pendente ou em conflito. Sair agora descartará a edição local. Deseja continuar?")) {
    discardPendingNoteDrafts(userId);
    navigate(to);
    return true;
  }
  return false;
}

export function useNotes(
  params: { node_id?: string; track_id?: string; include_deleted?: boolean },
  enabled = true,
) {
  return useQuery({
    queryKey: ["notes", params.node_id || params.track_id || "all", !!params.include_deleted],
    enabled,
    queryFn: () => api.get<StudyNote[]>("/notes", { params }).then((r) => r.data),
  });
}

export function useAutosaveNote(
  nodeId: string,
  blockId: string | null,
  initial: StudyNote | undefined,
  ready: boolean,
  userId = "anonymous",
) {
  const qc = useQueryClient();
  const identity = `${userId}:${nodeId}:${blockId || "node"}`;
  const initialServerBody = initial?.deleted ? "" : initial?.body || "";
  const recovered = pendingNoteDrafts.get(identity);
  const recoverDraft = recovered && !(ready && initialServerBody === recovered.body) ? recovered : undefined;
  const recoveredConflict = ready && recoverDraft && recoverDraft.version !== (initial?.version || 0)
    && initialServerBody !== recoverDraft.body ? { current: initial || null } : null;
  const [body, setBodyState] = useState(recoverDraft?.body ?? initialServerBody);
  const initialSaveState: NoteSaveState = recoveredConflict ? "conflict" : recoverDraft ? "pending" : "saved";
  const [state, setState] = useState<NoteSaveState>(initialSaveState);
  const [conflict, setConflict] = useState<NoteConflict | null>(recoveredConflict);
  const bodyRef = useRef(body);
  const initialRef = useRef(initial);
  initialRef.current = initial;
  const savedBodyRef = useRef(recoverDraft?.savedBody ?? initialServerBody);
  const versionRef = useRef(recoverDraft?.version ?? initial?.version ?? 0);
  const dirtyRef = useRef(!!recoverDraft && recoverDraft.body !== recoverDraft.savedBody);
  const stateRef = useRef<NoteSaveState>(initialSaveState);
  const conflictRef = useRef<NoteConflict | null>(recoveredConflict);
  const inFlightRef = useRef<Promise<boolean> | null>(null);
  const flushRef = useRef<NoteFlush>(() => Promise.resolve(true));
  const initializedIdentityRef = useRef(identity);
  const mountedRef = useRef(true);
  const flushRegistrationRef = useRef(Symbol(identity));
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const setSaveState = (next: NoteSaveState) => {
    stateRef.current = next;
    if (mountedRef.current) setState(next);
  };

  const syncDraft = useCallback(() => {
    if (dirtyRef.current) {
      discardedNoteDrafts.delete(identity);
      pendingNoteDrafts.set(identity, {
        identity, userId, nodeId, blockId, body: bodyRef.current,
        savedBody: savedBodyRef.current, version: versionRef.current,
      });
    } else {
      pendingNoteDrafts.delete(identity);
    }
  }, [blockId, identity, nodeId, userId]);

  useEffect(() => {
    mountedRef.current = true;
    return () => { mountedRef.current = false; };
  }, []);

  useEffect(() => {
    if (ready && recovered && initialServerBody === recovered.body
      && pendingNoteDrafts.get(identity) === recovered) {
      pendingNoteDrafts.delete(identity);
    }
  }, [identity, initialServerBody, ready, recovered]);

  useEffect(() => {
    if (!ready) return;
    const serverBody = initial?.deleted ? "" : initial?.body || "";
    const serverVersion = initial?.version || 0;
    if (initializedIdentityRef.current !== identity) {
      initializedIdentityRef.current = identity;
      bodyRef.current = serverBody;
      savedBodyRef.current = serverBody;
      versionRef.current = serverVersion;
      dirtyRef.current = false;
      conflictRef.current = null;
      setConflict(null);
      setBodyState(serverBody);
      setSaveState("saved");
      syncDraft();
      return;
    }
    if (serverVersion === versionRef.current) return;
    if (!dirtyRef.current && !inFlightRef.current) {
      bodyRef.current = serverBody;
      savedBodyRef.current = serverBody;
      versionRef.current = serverVersion;
      setBodyState(serverBody);
      setSaveState("saved");
      syncDraft();
    } else if (serverBody === bodyRef.current) {
      savedBodyRef.current = serverBody;
      versionRef.current = serverVersion;
      dirtyRef.current = false;
      setSaveState("saved");
      syncDraft();
    } else {
      const nextConflict = { current: initialRef.current || null };
      conflictRef.current = nextConflict;
      setConflict(nextConflict);
      setSaveState("conflict");
    }
  }, [identity, initial?.body, initial?.deleted, initial?.version, ready, syncDraft]);

  const flush = useCallback(async (): Promise<boolean> => {
    if (inFlightRef.current) {
      const priorResult = await inFlightRef.current;
      if (!priorResult) return false;
      return dirtyRef.current && !conflictRef.current ? flushRef.current() : !dirtyRef.current;
    }
    if (conflictRef.current) return false;
    if (!dirtyRef.current) return true;

    const submittedBody = bodyRef.current;
    const expectedVersion = versionRef.current;
    setSaveState("saving");
    const request = (async () => {
      try {
        const response = await api.put<NoteWriteResult>("/notes", {
          node_id: nodeId,
          block_id: blockId,
          body: submittedBody,
          expected_version: expectedVersion,
        });
        const saved = response.data;
        const serverBody = noteBody(saved);
        versionRef.current = saved.version;
        savedBodyRef.current = serverBody;
        if (bodyRef.current === submittedBody) {
          bodyRef.current = serverBody;
          dirtyRef.current = false;
          setBodyState(serverBody);
          setSaveState("saved");
        } else {
          dirtyRef.current = true;
          setSaveState("pending");
        }
        syncDraft();
        qc.invalidateQueries({ queryKey: ["notes"] });
        return true;
      } catch (error) {
        const detail = (error as NoteError).response?.data?.error?.details;
        if (detail?.code === "note_version_conflict") {
          const current = detail.current || null;
          const remoteBody = current?.deleted ? "" : current?.body || "";
          if (remoteBody === submittedBody) {
            versionRef.current = current?.version || 0;
            savedBodyRef.current = remoteBody;
            if (bodyRef.current === submittedBody) {
              dirtyRef.current = false;
              setSaveState("saved");
            } else {
              dirtyRef.current = true;
              setSaveState("pending");
            }
            syncDraft();
            qc.invalidateQueries({ queryKey: ["notes"] });
            return true;
          }
          const nextConflict = { current };
          conflictRef.current = nextConflict;
          setConflict(nextConflict);
          setSaveState("conflict");
          syncDraft();
          return false;
        }
        dirtyRef.current = true;
        setSaveState("error");
        syncDraft();
        return false;
      }
    })();
    inFlightRef.current = request;
    const succeeded = await request;
    if (inFlightRef.current === request) inFlightRef.current = null;
    if (!succeeded) return false;
    if (dirtyRef.current && !conflictRef.current) return flushRef.current();
    return !dirtyRef.current;
  }, [blockId, nodeId, qc, syncDraft]);
  flushRef.current = flush;

  const setBody = useCallback((next: string) => {
    if (next === bodyRef.current) return;
    bodyRef.current = next;
    dirtyRef.current = next !== savedBodyRef.current;
    setBodyState(next);
    if (!dirtyRef.current) {
      conflictRef.current = null;
      setConflict(null);
      setSaveState("saved");
    } else if (!conflictRef.current) {
      setSaveState("pending");
    }
    syncDraft();
  }, [syncDraft]);

  const retry = useCallback(() => {
    if (conflictRef.current) return Promise.resolve(false);
    dirtyRef.current = bodyRef.current !== savedBodyRef.current;
    if (dirtyRef.current) setSaveState("pending");
    return flushRef.current();
  }, []);

  const reloadServerVersion = useCallback(() => {
    const current = conflictRef.current?.current;
    const serverBody = current?.deleted ? "" : current?.body || "";
    bodyRef.current = serverBody;
    savedBodyRef.current = serverBody;
    versionRef.current = current?.version || 0;
    dirtyRef.current = false;
    conflictRef.current = null;
    setConflict(null);
    setBodyState(serverBody);
    setSaveState("saved");
    syncDraft();
  }, [syncDraft]);

  const overwriteServerVersion = useCallback(() => {
    const current = conflictRef.current?.current;
    versionRef.current = current?.version || 0;
    savedBodyRef.current = current?.deleted ? "" : current?.body || "";
    conflictRef.current = null;
    setConflict(null);
    dirtyRef.current = bodyRef.current !== savedBodyRef.current;
    if (!dirtyRef.current) {
      setSaveState("saved");
      syncDraft();
      return Promise.resolve(true);
    }
    setSaveState("pending");
    syncDraft();
    return flushRef.current();
  }, [syncDraft]);

  useEffect(() => {
    if (!ready || !dirtyRef.current || conflictRef.current) return;
    timerRef.current = setTimeout(() => { void flushRef.current(); }, 800);
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
      timerRef.current = null;
    };
  }, [body, ready]);

  useEffect(() => {
    const key = flushRegistrationRef.current;
    pendingNoteFlushes.set(key, { identity, userId, flush: () => flushRef.current() });
    return () => {
      pendingNoteFlushes.delete(key);
      if (discardedNoteDrafts.delete(identity)) {
        pendingNoteDrafts.delete(identity);
      } else if (dirtyRef.current) {
        syncDraft();
        void flushRef.current();
      }
    };
  }, [identity, syncDraft, userId]);

  return { body, setBody, state, conflict, retry, reloadServerVersion, overwriteServerVersion };
}

export function PendingNoteNavigationGuard() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const userId = user && typeof user === "object" ? user.id : undefined;
  useEffect(() => {
    if (userId) discardPendingNoteDraftsExcept(userId);
  }, [userId]);
  useEffect(() => {
    const onClick = (event: MouseEvent) => {
      if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      const target = event.target;
      if (!(target instanceof Element)) return;
      const anchor = target.closest<HTMLAnchorElement>("a[href]");
      if (!anchor || anchor.target && anchor.target !== "_self" || anchor.hasAttribute("download")) return;
      const destination = new URL(anchor.href, window.location.href);
      if (destination.origin !== window.location.origin) return;
      if (destination.pathname === window.location.pathname && destination.search === window.location.search && !destination.hash) return;
      if (!userId) return;
      if (!pendingNoteFlushes.size) return;
      event.preventDefault();
      void navigateAfterNoteSave(
        (to) => navigate(to),
        `${destination.pathname}${destination.search}${destination.hash}`,
        userId,
      );
    };
    const warnBeforeLeave = (event: BeforeUnloadEvent) => {
      if (!pendingNoteDrafts.size) return;
      event.preventDefault();
      event.returnValue = "";
    };
    document.addEventListener("click", onClick, true);
    window.addEventListener("beforeunload", warnBeforeLeave);
    return () => {
      document.removeEventListener("click", onClick, true);
      window.removeEventListener("beforeunload", warnBeforeLeave);
    };
  }, [navigate, userId]);
  return null;
}

export function useReviews(status = "pending") {
  return useQuery({ queryKey: ["reviews", status], queryFn: () => api.get<Review[]>("/reviews", { params: { status } }).then((r) => r.data) });
}

export function useScheduleReview() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: { node_id: string; block_id?: string | null; when: string; due_at?: string }) => api.post<Review>("/reviews", body).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["reviews"] }),
  });
}

export function useMySubmissions(nodeId?: string) {
  return useQuery({
    queryKey: ["submissions", "mine", nodeId || "all"],
    queryFn: () => api.get<Submission[]>("/submissions/mine", { params: { node_id: nodeId } }).then((r) => r.data),
  });
}
