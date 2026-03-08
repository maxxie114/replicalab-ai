import type {
  EpisodeState,
  ResetParams,
  ScientistAction,
  NegotiationMessage,
  ScoreBreakdown,
  JudgeAudit,
  PaperSummary,
  LabConstraints,
  BackendResetResponse,
  BackendStepResult,
  BackendObservation,
  BackendConversationEntry,
  BackendRewardBreakdown,
  BackendScenarioFamily,
  ScenarioTemplate,
  Difficulty,
  EpisodeStepTrace,
} from '@/types';

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api';
const WS_URL =
  import.meta.env.VITE_WS_URL ??
  `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws`;

function backendUnavailableMessage(context: string): string {
  return `${context}: backend unavailable at ${BASE_URL}. Start the API server with "python -m uvicorn server.app:app --host 127.0.0.1 --port 7860" and refresh.`;
}

function normalizeFetchError(error: unknown, context: string): Error {
  if (error instanceof Error && /Failed to fetch/i.test(error.message)) {
    return new Error(backendUnavailableMessage(context));
  }
  if (error instanceof Error) {
    return error;
  }
  return new Error(`${context}: unknown network error`);
}

// ---------------------------------------------------------------------------
// Adapter helpers: transform backend shapes into frontend types
// ---------------------------------------------------------------------------

function adaptConversation(entries: BackendConversationEntry[]): NegotiationMessage[] {
  return entries.map((e) => ({
    role: e.role as NegotiationMessage['role'],
    round: e.round_number,
    action_type: e.action_type ?? undefined,
    message: e.message,
    timestamp: Date.now(), // backend doesn't provide timestamps
  }));
}

function adaptRewardBreakdown(rb: BackendRewardBreakdown, totalReward: number): ScoreBreakdown {
  const penaltyEntries = Object.entries(rb.penalties);
  const penaltyTotal = penaltyEntries.reduce((sum, [, v]) => sum + v, 0);
  return {
    rigor: rb.rigor,
    feasibility: rb.feasibility,
    fidelity: rb.fidelity,
    parsimony: rb.parsimony,
    total_reward: totalReward,
    efficiency_bonus: rb.efficiency_bonus,
    communication_bonus: rb.communication_bonus,
    penalties: penaltyTotal,
    penalty_reasons: penaltyEntries.map(([k, v]) => `${k}: ${v}`),
  };
}

function adaptPaper(obs: BackendObservation): PaperSummary {
  const sci = obs.scientist!;
  // The backend doesn't return original protocol values separately.
  // We extract what's available from the scientist observation and use
  // sensible defaults for the "original" paper protocol fields.
  return {
    title: sci.paper_title,
    hypothesis: sci.paper_hypothesis,
    method: sci.paper_method,
    key_finding: sci.paper_key_finding,
    original_sample_size: sci.current_protocol?.sample_size ?? 0,
    original_technique: sci.current_protocol?.technique ?? 'N/A',
    original_controls: sci.current_protocol?.controls ?? [],
    original_duration_days: sci.current_protocol?.duration_days ?? 0,
  };
}

function adaptLabConstraints(obs: BackendObservation): LabConstraints {
  const lab = obs.lab_manager!;
  return {
    budget: lab.budget_total,
    budget_remaining: lab.budget_remaining,
    equipment_available: lab.equipment_available,
    reagents_available: lab.reagents_in_stock,
    staff_count: lab.staff_count,
    booking_conflicts: lab.equipment_booked,
    safety_rules: lab.safety_restrictions,
    time_limit_days: lab.time_limit_days,
  };
}

function observationToEpisodeState(
  obs: BackendObservation,
  sessionId: string,
  episodeId: string,
  seed: number,
  template: ScenarioTemplate,
  difficulty: Difficulty,
): EpisodeState {
  const sci = obs.scientist!;
  return {
    episode_id: episodeId,
    session_id: sessionId,
    seed,
    template,
    difficulty,
    round: sci.round_number,
    max_rounds: sci.max_rounds,
    done: false,
    paper: adaptPaper(obs),
    lab_constraints: adaptLabConstraints(obs),
    protocol: sci.current_protocol,
    conversation: adaptConversation(sci.conversation_history),
    scores: null,
    judge_audit: null,
    cumulative_reward: 0,
    step_history: [],
  };
}

function buildRoundTrace(
  prevState: EpisodeState,
  data: BackendStepResult,
): EpisodeStepTrace {
  const round = data.info.round;
  const rawHistory = data.observation?.scientist?.conversation_history ?? [];
  const roundEntries = rawHistory.filter((entry) => entry.round_number === round);
  const scientistEntry = roundEntries.find((entry) => entry.role === 'scientist');
  const labManagerEntry = roundEntries.find((entry) => entry.role === 'lab_manager');

  return {
    round,
    reward: data.reward,
    cumulative_reward: data.info.cumulative_reward ?? prevState.cumulative_reward + data.reward,
    action_type: scientistEntry?.action_type ?? 'unknown',
    scientist_message: scientistEntry?.message ?? '',
    lab_manager_action_type: labManagerEntry?.action_type ?? undefined,
    lab_manager_message: labManagerEntry?.message ?? undefined,
    step_reward_components: data.info.step_reward_components ?? {},
    protocol: data.observation?.scientist?.current_protocol ?? prevState.protocol,
    oracle_round_score: data.info.oracle_round_score ?? null,
    oracle_post_mortem: data.info.oracle_post_mortem ?? null,
    oracle_event: data.info.oracle_event ?? null,
  };
}

// ---------------------------------------------------------------------------
// REST API functions
// ---------------------------------------------------------------------------

export async function healthCheck(): Promise<{ status: string }> {
  try {
    const res = await fetch(`${BASE_URL}/health`);
    if (!res.ok) {
      throw new Error(`Health check failed: ${res.status}`);
    }
    return res.json();
  } catch (error) {
    throw normalizeFetchError(error, 'Health check failed');
  }
}

export async function getScenarios(): Promise<BackendScenarioFamily[]> {
  try {
    const res = await fetch(`${BASE_URL}/scenarios`);
    if (!res.ok) throw new Error('Failed to fetch scenarios');
    const data = await res.json();
    return data.scenarios;
  } catch (error) {
    throw normalizeFetchError(error, 'Failed to fetch scenarios');
  }
}

export async function resetEpisode(params: ResetParams): Promise<EpisodeState> {
  const seed = params.seed ?? Math.floor(Math.random() * 10000);
  const template = params.template ?? 'math_reasoning';
  const difficulty = params.difficulty ?? 'easy';

  try {
    const res = await fetch(`${BASE_URL}/reset`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ seed, scenario: template, difficulty }),
    });
    if (!res.ok) {
      const text = await res.text();
      throw new Error(`Failed to reset episode: ${text}`);
    }
    const data: BackendResetResponse = await res.json();
    return observationToEpisodeState(
      data.observation,
      data.session_id,
      data.episode_id,
      seed,
      template,
      difficulty,
    );
  } catch (error) {
    throw normalizeFetchError(error, 'Failed to reset episode');
  }
}

export async function stepEpisode(
  sessionId: string,
  action: ScientistAction,
  prevState: EpisodeState,
): Promise<EpisodeState> {
  let data: BackendStepResult;
  try {
    const res = await fetch(`${BASE_URL}/step`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, action }),
    });
    if (!res.ok) {
      const text = await res.text();
      throw new Error(`Failed to step episode: ${text}`);
    }
    data = await res.json();
  } catch (error) {
    throw normalizeFetchError(error, 'Failed to step episode');
  }
  const info = data.info;

  // Build scores if done and reward breakdown is available
  let scores: ScoreBreakdown | null = null;
  let judgeAudit: JudgeAudit | null = null;
  if (data.done && info.reward_breakdown) {
    scores = adaptRewardBreakdown(info.reward_breakdown, data.reward);
    judgeAudit = {
      verdict: info.verdict ?? 'unknown',
      judge_notes: info.judge_notes ? [info.judge_notes] : [],
      top_failure_reasons: info.top_failure_reasons,
      score_breakdown: scores,
    };
  }

  // Get updated conversation from the observation
  const obs = data.observation;
  const conversation = obs?.scientist
    ? adaptConversation(obs.scientist.conversation_history)
    : prevState.conversation;
  const protocol = obs?.scientist?.current_protocol ?? prevState.protocol;
  const round = obs?.scientist?.round_number ?? prevState.round + 1;
  const cumulativeReward = data.info.cumulative_reward ?? prevState.cumulative_reward + data.reward;

  // Update lab constraints if available
  const labConstraints = obs ? adaptLabConstraints(obs) : prevState.lab_constraints;
  const roundTrace = buildRoundTrace(prevState, data);

  return {
    ...prevState,
    round,
    done: data.done,
    protocol,
    conversation,
    lab_constraints: labConstraints,
    scores,
    judge_audit: judgeAudit,
    cumulative_reward: cumulativeReward,
    step_history: [...prevState.step_history, roundTrace],
  };
}

export async function getReplay(episodeId: string): Promise<unknown> {
  try {
    const res = await fetch(`${BASE_URL}/replay/${episodeId}`);
    if (!res.ok) throw new Error('Failed to fetch replay');
    return res.json();
  } catch (error) {
    throw normalizeFetchError(error, 'Failed to fetch replay');
  }
}

// ---------------------------------------------------------------------------
// WebSocket support
// ---------------------------------------------------------------------------

export type WebSocketMessage =
  | { type: 'reset'; params: ResetParams }
  | { type: 'step'; action: ScientistAction }
  | { type: 'state' };

export type WebSocketResponse =
  | { type: 'reset_ok'; episode_id: string; observation: BackendObservation }
  | { type: 'step_ok'; observation: BackendObservation | null; reward: number; done: boolean; info: Record<string, unknown> }
  | { type: 'pong' }
  | { type: 'error'; message: string };

export function createWebSocket(
  onMessage: (msg: WebSocketResponse) => void,
  onOpen?: () => void,
  onClose?: () => void,
  onError?: (err: Event) => void,
): WebSocket {
  const ws = new WebSocket(WS_URL);

  ws.onopen = () => onOpen?.();
  ws.onclose = () => onClose?.();
  ws.onerror = (e) => onError?.(e);
  ws.onmessage = (event) => {
    try {
      const msg = JSON.parse(event.data) as WebSocketResponse;
      onMessage(msg);
    } catch {
      console.error('Failed to parse WebSocket message:', event.data);
    }
  };

  return ws;
}

export function sendWsMessage(ws: WebSocket, msg: WebSocketMessage) {
  if (ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify(msg));
  }
}

// ---------------------------------------------------------------------------
// Default scientist action (for auto-step)
// ---------------------------------------------------------------------------

export function buildDefaultScientistAction(state?: EpisodeState): ScientistAction {
  const durationLimit = Math.max(1, state?.lab_constraints.time_limit_days ?? 3);
  const template = state?.template;
  const currentProtocol = state?.protocol;

  const originalDuration = state?.paper.original_duration_days ?? 0;
  const preferredDuration = currentProtocol?.duration_days ?? (originalDuration || durationLimit);
  const durationDays = Math.max(
    1,
    Math.min(durationLimit, preferredDuration),
  );

  const technique =
    currentProtocol?.technique
      ?? (state?.paper.original_technique && state.paper.original_technique !== 'N/A'
        ? state.paper.original_technique
        : template === 'math_reasoning'
          ? 'structured_proof_check'
          : template === 'finance_trading'
            ? 'offline_backtest'
            : 'published_training_recipe');

  const controls =
    currentProtocol?.controls.length
      ? currentProtocol.controls
      : state?.paper.original_controls.length
        ? state.paper.original_controls
        : ['baseline'];

  const baseSampleSize = currentProtocol?.sample_size ?? 3;
  const sampleSize =
    state?.round && state.round > 0
      ? Math.max(3, Math.min(baseSampleSize + (state.round % 2 === 0 ? 1 : -1), 12))
      : template === 'math_reasoning'
        ? 4
        : 3;

  const requiredEquipment = currentProtocol?.required_equipment.length
    ? currentProtocol.required_equipment
    : state?.lab_constraints.equipment_available.slice(0, 1) ?? [];
  const requiredReagents = currentProtocol?.required_reagents.length
    ? currentProtocol.required_reagents
    : state?.lab_constraints.reagents_available.slice(0, 1) ?? [];

  return {
    action_type: currentProtocol ? 'revise_protocol' : 'propose_protocol',
    sample_size: sampleSize,
    controls,
    technique,
    duration_days: durationDays,
    required_equipment: requiredEquipment,
    required_reagents: requiredReagents,
    questions: [],
    rationale: currentProtocol
      ? `Refine the existing protocol for round ${state?.round ?? 0} while staying inside the ${durationLimit}-day lab window.`
      : `Replicate the source result within the available lab window of ${durationLimit} days using currently available resources.`,
  };
}

export function buildAcceptAction(): ScientistAction {
  return {
    action_type: 'accept',
    sample_size: 0,
    controls: [],
    technique: '',
    duration_days: 0,
    required_equipment: [],
    required_reagents: [],
    questions: [],
    rationale: '',
  };
}
