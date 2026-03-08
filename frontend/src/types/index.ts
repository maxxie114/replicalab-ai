export type ActionType = 'propose_protocol' | 'revise_protocol' | 'request_info' | 'accept';
export type LabManagerActionType = 'report_feasibility' | 'suggest_substitution' | 'reject' | 'accept';
export type Difficulty = 'easy' | 'medium' | 'hard';
export type ScenarioTemplate = 'cell_biology' | 'ml_benchmark' | 'behavioral_psych';
export type Role = 'scientist' | 'lab_manager' | 'judge';

export interface ScientistAction {
  action_type: ActionType;
  sample_size?: number;
  controls?: string[];
  technique?: string;
  duration_days?: number;
  required_equipment?: string[];
  required_reagents?: string[];
  questions?: string[];
  rationale?: string;
}

export interface LabManagerAction {
  action_type: LabManagerActionType;
  feasibility_report?: FeasibilityReport;
  suggested_changes?: SuggestedChange[];
  message?: string;
}

export interface FeasibilityReport {
  budget_ok: boolean;
  equipment_ok: boolean;
  reagents_ok: boolean;
  schedule_ok: boolean;
  personnel_ok: boolean;
  issues: string[];
}

export interface SuggestedChange {
  field: string;
  original: string;
  suggested: string;
  reason: string;
}

export interface Protocol {
  sample_size: number;
  controls: string[];
  technique: string;
  duration_days: number;
  required_equipment: string[];
  required_reagents: string[];
}

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

export interface LabConstraints {
  budget: number;
  budget_remaining: number;
  equipment_available: string[];
  reagents_available: string[];
  staff_count: number;
  booking_conflicts: string[];
  safety_rules: string[];
}

export interface NegotiationMessage {
  role: Role;
  round: number;
  action: ScientistAction | LabManagerAction;
  message: string;
  timestamp: number;
}

export interface ScoreBreakdown {
  rigor: number;
  feasibility: number;
  fidelity: number;
  total_reward: number;
  efficiency_bonus: number;
  communication_bonus: number;
  penalties: number;
  penalty_reasons: string[];
}

export interface JudgeAudit {
  verdict: 'success' | 'partial' | 'failure';
  judge_notes: string[];
  top_failure_reasons: string[];
  score_breakdown: ScoreBreakdown;
}

export interface EpisodeState {
  episode_id: string;
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
}

export interface ResetParams {
  seed?: number;
  template?: ScenarioTemplate;
  difficulty?: Difficulty;
}

export interface StepResult {
  observation: Record<string, unknown>;
  reward: number;
  done: boolean;
  info: {
    round: number;
    scores?: ScoreBreakdown;
    judge_audit?: JudgeAudit;
  };
}

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
