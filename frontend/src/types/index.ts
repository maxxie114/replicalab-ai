export type ActionType = 'propose_protocol' | 'revise_protocol' | 'request_info' | 'accept';
export type LabManagerActionType = 'report_feasibility' | 'suggest_alternative' | 'reject' | 'accept';
export type Difficulty = 'easy' | 'medium' | 'hard';
export type ScenarioTemplate = 'math_reasoning' | 'ml_benchmark' | 'finance_trading';
export type Role = 'scientist' | 'lab_manager' | 'judge' | 'system';
export type DemoCase = 'fast-agreement' | 'learning-opportunity' | 'no-agreement';

// --- Backend-aligned action contracts ---

export interface ScientistAction {
  action_type: ActionType;
  sample_size: number;
  controls: string[];
  technique: string;
  duration_days: number;
  required_equipment: string[];
  required_reagents: string[];
  questions: string[];
  rationale: string;
}

export interface LabManagerAction {
  action_type: LabManagerActionType;
  feasible: boolean;
  budget_ok: boolean;
  equipment_ok: boolean;
  reagents_ok: boolean;
  schedule_ok: boolean;
  staff_ok: boolean;
  suggested_technique: string;
  suggested_sample_size: number;
  suggested_controls: string[];
  explanation: string;
}

// --- Protocol ---

export interface Protocol {
  sample_size: number;
  controls: string[];
  technique: string;
  duration_days: number;
  required_equipment: string[];
  required_reagents: string[];
  rationale: string;
}

// --- Paper summary (derived from ScientistObservation) ---

export interface PaperSummary {
  title: string;
  hypothesis: string;
  method: string;
  key_finding: string;
  original_sample_size: number;
  original_technique: string;
  original_controls: string[];
  original_duration_days: number;
}

// --- Lab constraints (derived from LabManagerObservation) ---

export interface LabConstraints {
  budget: number;
  budget_remaining: number;
  equipment_available: string[];
  reagents_available: string[];
  staff_count: number;
  booking_conflicts: string[];
  safety_rules: string[];
  time_limit_days: number;
}

// --- Conversation entry (matches backend ConversationEntry) ---

export interface NegotiationMessage {
  role: Role;
  round: number;
  action_type?: string;
  message: string;
  timestamp: number;
}

// --- Score breakdown (matches backend RewardBreakdown) ---

export interface ScoreBreakdown {
  rigor: number;
  feasibility: number;
  fidelity: number;
  parsimony: number;
  total_reward: number;
  efficiency_bonus: number;
  communication_bonus: number;
  penalties: number;
  penalty_reasons: string[];
}

// --- Judge audit (derived from StepInfo when done) ---

export interface JudgeAudit {
  verdict: string;
  judge_notes: string[];
  top_failure_reasons: string[];
  score_breakdown: ScoreBreakdown;
}

export interface EpisodeStepTrace {
  round: number;
  reward: number;
  cumulative_reward: number;
  action_type: string;
  scientist_message: string;
  lab_manager_action_type?: string;
  lab_manager_message?: string;
  step_reward_components: Record<string, number>;
  protocol: Protocol | null;
  oracle_round_score?: Record<string, unknown> | null;
  oracle_post_mortem?: Record<string, unknown> | null;
  oracle_event?: Record<string, unknown> | null;
}

// --- Frontend episode state (assembled from backend responses) ---

export interface EpisodeState {
  episode_id: string;
  session_id: string;
  seed: number;
  template: ScenarioTemplate;
  difficulty: Difficulty;
  round: number;
  max_rounds: number;
  done: boolean;
  paper: PaperSummary;
  lab_constraints: LabConstraints;
  protocol: Protocol | null;
  conversation: NegotiationMessage[];
  scores: ScoreBreakdown | null;
  judge_audit: JudgeAudit | null;
  cumulative_reward: number;
  step_history: EpisodeStepTrace[];
  demo_case?: DemoCase;
}

export interface ResetParams {
  seed?: number;
  template?: ScenarioTemplate;
  difficulty?: Difficulty;
}

// --- Backend response types ---

export interface BackendConversationEntry {
  role: string;
  message: string;
  round_number: number;
  action_type: string | null;
}

export interface BackendObservation {
  scientist: {
    paper_title: string;
    paper_hypothesis: string;
    paper_method: string;
    paper_key_finding: string;
    experiment_goal: string;
    conversation_history: BackendConversationEntry[];
    current_protocol: Protocol | null;
    round_number: number;
    max_rounds: number;
  } | null;
  lab_manager: {
    budget_total: number;
    budget_remaining: number;
    equipment_available: string[];
    equipment_booked: string[];
    reagents_in_stock: string[];
    reagents_out_of_stock: string[];
    staff_count: number;
    time_limit_days: number;
    safety_restrictions: string[];
    conversation_history: BackendConversationEntry[];
    current_protocol: Protocol | null;
    round_number: number;
    max_rounds: number;
  } | null;
}

export interface BackendResetResponse {
  session_id: string;
  episode_id: string;
  observation: BackendObservation;
}

export interface BackendRewardBreakdown {
  rigor: number;
  feasibility: number;
  fidelity: number;
  parsimony: number;
  efficiency_bonus: number;
  communication_bonus: number;
  penalties: Record<string, number>;
}

export interface BackendStepInfo {
  agreement_reached: boolean;
  error: string | null;
  reward_breakdown: BackendRewardBreakdown | null;
  judge_notes: string | null;
  verdict: string | null;
  top_failure_reasons: string[];
  round: number;
  episode_id: string;
  step_reward_components?: Record<string, number>;
  cumulative_reward?: number;
  oracle_round_score?: Record<string, unknown> | null;
  oracle_post_mortem?: Record<string, unknown> | null;
  oracle_event?: Record<string, unknown> | null;
}

export interface BackendStepResult {
  observation: BackendObservation | null;
  reward: number;
  done: boolean;
  info: BackendStepInfo;
}

export interface BackendScenarioFamily {
  family: string;
  difficulties: string[];
}

export interface BackendRuntimeStatus {
  scientist_runtime: string;
  scientist_model: string;
  scientist_ready: boolean;
  agent_step_available: boolean;
  available_runtimes: string[];
  note: string;
}

// --- Training metrics ---

export interface TrainingMetrics {
  episode: number;
  reward: number;
  rigor: number;
  feasibility: number;
  fidelity: number;
  rounds_used: number;
  agreement: boolean;
  invalid_actions: number;
}

export interface TrainingComparison {
  baseline: TrainingMetrics[];
  trained: TrainingMetrics[];
  summary: {
    baseline_avg_reward: number;
    trained_avg_reward: number;
    baseline_agreement_rate: number;
    trained_agreement_rate: number;
    baseline_avg_rounds: number;
    trained_avg_rounds: number;
    baseline_invalid_rate: number;
    trained_invalid_rate: number;
  };
}
