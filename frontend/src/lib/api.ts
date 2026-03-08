import type {
  EpisodeState,
  ResetParams,
  ScientistAction,
  NegotiationMessage,
  ScoreBreakdown,
  JudgeAudit,
  Protocol,
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
} from '@/types';

const BASE_URL = '/api';
const WS_URL = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws`;

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
  };
}

// ---------------------------------------------------------------------------
// REST API functions
// ---------------------------------------------------------------------------

export async function healthCheck(): Promise<{ status: string }> {
  const res = await fetch(`${BASE_URL}/health`);
  return res.json();
}

export async function getScenarios(): Promise<BackendScenarioFamily[]> {
  const res = await fetch(`${BASE_URL}/scenarios`);
  if (!res.ok) throw new Error('Failed to fetch scenarios');
  const data = await res.json();
  return data.scenarios;
}

export async function resetEpisode(params: ResetParams): Promise<EpisodeState> {
  const seed = params.seed ?? Math.floor(Math.random() * 10000);
  const template = params.template ?? 'math_reasoning';
  const difficulty = params.difficulty ?? 'easy';

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
}

export async function stepEpisode(
  sessionId: string,
  action: ScientistAction,
  prevState: EpisodeState,
): Promise<EpisodeState> {
  const res = await fetch(`${BASE_URL}/step`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, action }),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Failed to step episode: ${text}`);
  }
  const data: BackendStepResult = await res.json();
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

  // Update lab constraints if available
  const labConstraints = obs ? adaptLabConstraints(obs) : prevState.lab_constraints;

  return {
    ...prevState,
    round,
    done: data.done,
    protocol,
    conversation,
    lab_constraints: labConstraints,
    scores,
    judge_audit: judgeAudit,
  };
}

export async function getReplay(episodeId: string): Promise<unknown> {
  const res = await fetch(`${BASE_URL}/replay/${episodeId}`);
  if (!res.ok) throw new Error('Failed to fetch replay');
  return res.json();
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

export function buildDefaultScientistAction(): ScientistAction {
  return {
    action_type: 'propose_protocol',
    sample_size: 3,
    controls: ['baseline'],
    technique: 'standard',
    duration_days: 5,
    required_equipment: [],
    required_reagents: [],
    questions: [],
    rationale: 'Initial protocol proposal to begin negotiation.',
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
