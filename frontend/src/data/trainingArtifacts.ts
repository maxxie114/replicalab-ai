import type { TrainingComparison } from '@/types';

export interface TrainingCheckpoint {
  label: string;
  artifactStep: number;
  averageReward: number;
  agreementRate: number;
  averageRounds: number;
  rolloutsPerGroup: number;
  scenarioCount: number;
  finishedAt: string;
}

export interface TrainingLogRow {
  label: string;
  trainingStep: number;
  seed: number;
  paperTitle: string;
  reward: number;
  roundsUsed: number;
  invalidActionCount: number;
  parseErrorCount: number;
  verdict: string | null;
  note: string;
}

export interface PreviewArtifact {
  runName: string;
  modelName: string;
  datasetSize: number;
  evidencePackVersion: string;
  config: {
    maxSteps?: number;
    numTrainEpochs?: number;
    learningRate: number;
    loraRank: number;
    maxSeqLength: number;
    templates: string[];
    difficulties: string[];
  };
}

export interface PolicySnapshot {
  id: 'baseline' | 'trained' | 'oracle';
  label: string;
  scientistMode: string;
  labManagerMode: string;
  judgeMode: string;
  source: string;
  status: 'live' | 'artifact' | 'planned';
  averageReward: number | null;
  agreementRate: number | null;
  averageRounds: number | null;
  invalidRate: number | null;
  summary: string;
}

export const HOLDOUT_COMPARE: TrainingComparison = {
  baseline: [
    { episode: 1, reward: 4.925, rigor: 0.85, feasibility: 1.0, fidelity: 0.45, rounds_used: 2, agreement: true, invalid_actions: 0 },
    { episode: 2, reward: 4.925, rigor: 0.85, feasibility: 1.0, fidelity: 0.45, rounds_used: 2, agreement: true, invalid_actions: 0 },
    { episode: 3, reward: 4.925, rigor: 0.85, feasibility: 1.0, fidelity: 0.45, rounds_used: 2, agreement: true, invalid_actions: 0 },
    { episode: 4, reward: 4.925, rigor: 0.85, feasibility: 1.0, fidelity: 0.45, rounds_used: 2, agreement: true, invalid_actions: 0 },
  ],
  trained: [
    { episode: 1, reward: -5.0, rigor: 0.0, feasibility: 0.0, fidelity: 0.0, rounds_used: 20, agreement: false, invalid_actions: 20 },
    { episode: 2, reward: -4.0, rigor: 0.0, feasibility: 0.0, fidelity: 0.0, rounds_used: 20, agreement: false, invalid_actions: 20 },
    { episode: 3, reward: -5.0, rigor: 0.0, feasibility: 0.0, fidelity: 0.0, rounds_used: 20, agreement: false, invalid_actions: 20 },
    { episode: 4, reward: -4.0, rigor: 0.0, feasibility: 0.0, fidelity: 0.0, rounds_used: 20, agreement: false, invalid_actions: 20 },
  ],
  summary: {
    baseline_avg_reward: 4.925,
    trained_avg_reward: -4.5,
    baseline_agreement_rate: 1.0,
    trained_agreement_rate: 0.0,
    baseline_avg_rounds: 2.0,
    trained_avg_rounds: 20.0,
    baseline_invalid_rate: 0.0,
    trained_invalid_rate: 1.0,
  },
};

export const LIVE_CHECKPOINTS: TrainingCheckpoint[] = [
  {
    label: 'Checkpoint 1',
    artifactStep: 1,
    averageReward: -1.0,
    agreementRate: 0.0,
    averageRounds: 1.75,
    rolloutsPerGroup: 2,
    scenarioCount: 2,
    finishedAt: '2026-03-08T17:55:41.971589+00:00',
  },
  {
    label: 'Checkpoint 2',
    artifactStep: 2,
    averageReward: 0.387202,
    agreementRate: 0.25,
    averageRounds: 3.0,
    rolloutsPerGroup: 2,
    scenarioCount: 2,
    finishedAt: '2026-03-08T17:59:47.820056+00:00',
  },
  {
    label: 'Checkpoint 5',
    artifactStep: 5,
    averageReward: 0.596966,
    agreementRate: 0.305556,
    averageRounds: 3.055556,
    rolloutsPerGroup: 3,
    scenarioCount: 4,
    finishedAt: '2026-03-08T18:12:40.950355+00:00',
  },
];

export const TRAINING_LOG_ROWS: TrainingLogRow[] = [
  {
    label: 'clean_accept_seed0_step1',
    trainingStep: 1,
    seed: 0,
    paperTitle: 'Reproducing a CIFAR-10 ResNet-18 baseline',
    reward: 4.54881,
    roundsUsed: 3,
    invalidActionCount: 0,
    parseErrorCount: 0,
    verdict: 'accept',
    note: 'The policy produced a valid protocol and reached a clean judged acceptance.',
  },
  {
    label: 'ag_news_invalids_step1',
    trainingStep: 1,
    seed: 1,
    paperTitle: 'Reproducing an AG News TinyBERT baseline',
    reward: -0.25,
    roundsUsed: 4,
    invalidActionCount: 4,
    parseErrorCount: 0,
    verdict: null,
    note: 'The main failure mode was repeated invalid actions on the medium AG News case.',
  },
  {
    label: 'diffusion_parse_failure_step2',
    trainingStep: 2,
    seed: 2,
    paperTitle: 'Reproducing an AG News TinyBERT baseline',
    reward: -1.0,
    roundsUsed: 2,
    invalidActionCount: 0,
    parseErrorCount: 1,
    verdict: null,
    note: 'Parser instability still caused zero-score rollouts after training had already begun.',
  },
  {
    label: 'checkpoint5_best_snapshot',
    trainingStep: 5,
    seed: 0,
    paperTitle: 'replicalab-scientist-art-live:step5',
    reward: 0.596966,
    roundsUsed: 3,
    invalidActionCount: 0,
    parseErrorCount: 0,
    verdict: 'mixed',
    note: 'By checkpoint 5 the live run had moved into positive average reward, but not enough to beat baseline on hold-out compare.',
  },
];

export const SCIENTIST_PREVIEW_ARTIFACT: PreviewArtifact = {
  runName: 'scientist-preview-smoke-20260308b',
  modelName: 'Qwen/Qwen3-8B',
  datasetSize: 18,
  evidencePackVersion: '6a0802447dc4',
  config: {
    maxSteps: 12,
    learningRate: 5e-6,
    loraRank: 32,
    maxSeqLength: 4096,
    templates: ['math_reasoning', 'ml_benchmark', 'finance_trading'],
    difficulties: ['easy', 'medium', 'hard'],
  },
};

export const LAB_MANAGER_PREVIEW_ARTIFACT: PreviewArtifact = {
  runName: 'lab-manager-preview-smoke-20260308b',
  modelName: 'Qwen/Qwen3-8B',
  datasetSize: 54,
  evidencePackVersion: '6a0802447dc4',
  config: {
    numTrainEpochs: 1.0,
    learningRate: 2e-5,
    loraRank: 32,
    maxSeqLength: 3072,
    templates: ['math_reasoning', 'ml_benchmark', 'finance_trading'],
    difficulties: ['easy', 'medium', 'hard'],
  },
};

export const LOCAL_BASELINE_SUMMARY = {
  averageReward: 4.600926,
  agreementRate: 1.0,
  averageRounds: 2.0,
  averageRigor: 0.805556,
  averageFeasibility: 1.0,
  averageFidelity: 0.438889,
  episodeCount: 3,
};

export const TRAINING_ASSESSMENT = {
  needsMoreTraining: true,
  achieved: [
    'The minimal Colab path and the reusable training modules are both in place.',
    'Scientist preview data and Lab Manager preview data were generated successfully on the frozen evidence packs.',
    'The live ART/OpenEnv Scientist run reached positive average reward by checkpoint 5.',
  ],
  gaps: [
    'Hold-out compare still strongly favors the deterministic baseline over the trained scientist policy.',
    'Invalid-action rate on the hold-out compare is still 1.0 for the trained policy.',
    'Lab Manager has preview artifacts but does not yet have a live trained-and-evaluated adapter in the demo.',
  ],
  improvements: [
    'Reduce invalid JSON and invalid action rate before extending training length.',
    'Run more train steps on the same frozen evidence version and compare on fixed held-out seeds after each checkpoint.',
    'Add curriculum or parser-focused reward shaping for the medium ML benchmark cases.',
    'Finish the Lab Manager SFT run and evaluate Scientist-plus-Lab-Manager together instead of only Scientist RL.',
  ],
};

export const POLICY_COMPARE: PolicySnapshot[] = [
  {
    id: 'baseline',
    label: 'Baseline runtime',
    scientistMode: 'Deterministic frontend action builder, not a mounted LLM adapter',
    labManagerMode: 'Deterministic feasibility pipeline in the backend',
    judgeMode: 'Deterministic rubric and audit',
    source: 'Live runtime and local baseline evaluation',
    status: 'live',
    averageReward: HOLDOUT_COMPARE.summary.baseline_avg_reward,
    agreementRate: HOLDOUT_COMPARE.summary.baseline_agreement_rate,
    averageRounds: HOLDOUT_COMPARE.summary.baseline_avg_rounds,
    invalidRate: HOLDOUT_COMPARE.summary.baseline_invalid_rate,
    summary:
      'This is the policy path used by the current /compare page. It reaches agreement reliably and stays fully judge-grounded, but it is not yet using the trained Scientist adapter.',
  },
  {
    id: 'trained',
    label: 'Trained Scientist',
    scientistMode: 'Artifact-backed Scientist RL adapter evaluation',
    labManagerMode: 'Deterministic feasibility pipeline in the backend',
    judgeMode: 'Deterministic rubric and audit',
    source: 'Hold-out compare artifact from the training pipeline',
    status: 'artifact',
    averageReward: HOLDOUT_COMPARE.summary.trained_avg_reward,
    agreementRate: HOLDOUT_COMPARE.summary.trained_agreement_rate,
    averageRounds: HOLDOUT_COMPARE.summary.trained_avg_rounds,
    invalidRate: HOLDOUT_COMPARE.summary.trained_invalid_rate,
    summary:
      'The training pipeline ran successfully, but this adapter still underperforms the baseline badly on held-out seeded evaluation because invalid actions remain too high.',
  },
  {
    id: 'oracle',
    label: 'Oracle-assisted V2',
    scientistMode: 'Planned Anthropic-assisted path, not mounted in the public runtime',
    labManagerMode: 'Optional oracle narration and post-mortem path exists in code, not live in demo runtime',
    judgeMode: 'Still deterministic even when oracle features are enabled',
    source: 'Architecture target only, no committed evaluation artifact yet',
    status: 'planned',
    averageReward: null,
    agreementRate: null,
    averageRounds: null,
    invalidRate: null,
    summary:
      'The oracle path exists in the codebase as a V2 extension, but there is no live public run or artifact-backed benchmark result wired into the app yet, so we should not claim oracle gains here.',
  },
];

export const CURRENT_RUNTIME_MODEL_STATUS = {
  comparePageUsesLiveModel: false,
  episodePageUsesLiveModel: false,
  backendUsesOracle: false,
  backendUsesDeterministicLabManager: true,
  backendUsesDeterministicJudge: true,
  note:
    'Right now the public demo runtime is not loading a trained Scientist adapter or an Anthropic oracle. The Scientist moves come from the frontend default action builder or the protocol editor, while the backend Lab Manager and Judge stay deterministic.',
};
