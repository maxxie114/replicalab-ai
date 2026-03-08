import type { DemoCase, EpisodeState, ScientistAction } from '@/types';
import { buildAcceptAction, buildDefaultScientistAction } from '@/lib/api';

export interface DemoCaseMeta {
  id: DemoCase;
  title: string;
  subtitle: string;
  summary: string;
  seed: number;
}

export const DEMO_CASES: DemoCaseMeta[] = [
  {
    id: 'fast-agreement',
    title: 'Scenario 1: First-Round Agreement',
    subtitle: 'Good paper, fast agreement',
    summary: 'A strong paper-derived benchmark where the first protocol is feasible and the agents converge immediately.',
    seed: 101,
  },
  {
    id: 'learning-opportunity',
    title: 'Scenario 2: Multi-Round Learning',
    subtitle: 'Heavy RL learning opportunity',
    summary: 'The Scientist starts overly ambitious, absorbs constraint feedback across several rounds, then lands on a feasible protocol.',
    seed: 202,
  },
  {
    id: 'no-agreement',
    title: 'Scenario 3: No Agreement',
    subtitle: 'Reject, not replicable under current setup',
    summary: 'The protocol never becomes acceptable within the six-round budget, producing a clean rejection case for the demo.',
    seed: 303,
  },
];

const LIVE_TEMPLATES = ['math_reasoning', 'ml_benchmark', 'finance_trading'] as const;
const LIVE_DIFFICULTIES = ['easy', 'medium', 'medium', 'hard'] as const;

function sampleRandom<T>(items: readonly T[]): T {
  return items[Math.floor(Math.random() * items.length)];
}

export function buildLiveEpisodePath(): string {
  const template = sampleRandom(LIVE_TEMPLATES);
  const difficulty = sampleRandom(LIVE_DIFFICULTIES);
  const seed = Math.floor(Math.random() * 9000) + 1000;
  return `/episode?template=${template}&difficulty=${difficulty}&seed=${seed}&autostart=1&autoplay=1`;
}

export function parseDemoCase(value: string | null): DemoCase | undefined {
  return DEMO_CASES.find((item) => item.id === value)?.id;
}

function buildScenarioAwareProposal(
  state: EpisodeState,
  overrides: Partial<ScientistAction>,
): ScientistAction {
  const baseAction = buildDefaultScientistAction(state);
  const actionType = state.protocol ? 'revise_protocol' : 'propose_protocol';

  return {
    ...baseAction,
    action_type: actionType,
    ...overrides,
  };
}

export function buildDemoScientistAction(
  state: EpisodeState,
  demoCase?: DemoCase,
): ScientistAction {
  if (!demoCase) {
    return state.round >= state.max_rounds - 1
      ? buildAcceptAction()
      : buildDefaultScientistAction(state);
  }

  const defaultEquipment = state.lab_constraints.equipment_available.slice(0, 1);
  const defaultReagents = state.lab_constraints.reagents_available.slice(0, 1);
  const defaultTechnique =
    state.protocol?.technique ||
    (state.paper.original_technique !== 'N/A'
      ? state.paper.original_technique
      : 'published_training_recipe');

  if (demoCase === 'fast-agreement') {
    if (state.round >= 1) {
      return buildAcceptAction();
    }
    return buildScenarioAwareProposal(state, {
      sample_size: 3,
      controls: ['baseline'],
      technique: defaultTechnique,
      duration_days: Math.min(4, state.lab_constraints.time_limit_days),
      required_equipment: defaultEquipment,
      required_reagents: defaultReagents,
      rationale: 'Reproduce the published baseline exactly once with the available reviewer pass and hardware.',
    });
  }

  if (demoCase === 'learning-opportunity') {
    const learningPlan: Record<number, Partial<ScientistAction>> = {
      0: {
        sample_size: 96,
        controls: ['baseline', 'ablation', 'sanity_check'],
        rationale: 'Start with an expansive benchmark reproduction to maximize coverage before trimming.',
      },
      1: {
        sample_size: 72,
        controls: ['baseline', 'ablation', 'sanity_check'],
        rationale: 'Reduce the experimental load, but keep the extra controls while the constraints are still being learned.',
      },
      2: {
        sample_size: 48,
        controls: ['baseline', 'ablation', 'sanity_check'],
        rationale: 'Continue lowering the sample size while preserving the full validation set of controls.',
      },
      3: {
        sample_size: 32,
        controls: ['baseline', 'ablation', 'sanity_check'],
        rationale: 'The Scientist now converges toward feasibility by balancing budget with stronger controls.',
      },
      4: {
        sample_size: 24,
        controls: ['baseline', 'ablation'],
        rationale: 'Final revision: keep the baseline plus one ablation and fit the protocol cleanly inside the lab capacity.',
      },
    };

    if (state.round >= 5) {
      return buildAcceptAction();
    }
    return buildScenarioAwareProposal(state, {
      technique: defaultTechnique,
      duration_days: Math.min(4, state.lab_constraints.time_limit_days),
      required_equipment: defaultEquipment,
      required_reagents: defaultReagents,
      ...learningPlan[state.round],
    });
  }

  const rejectionPlan: Record<number, Partial<ScientistAction>> = {
    0: {
      sample_size: 96,
      controls: ['baseline', 'ablation', 'sanity_check'],
      rationale: 'Push for the full benchmark replication despite the current resource limits.',
    },
    1: {
      sample_size: 88,
      controls: ['baseline', 'ablation', 'sanity_check'],
      rationale: 'Trim slightly, but keep the high-coverage plan intact.',
    },
    2: {
      sample_size: 80,
      controls: ['baseline', 'ablation', 'sanity_check'],
      rationale: 'Still prioritize coverage over the budget warnings.',
    },
    3: {
      sample_size: 76,
      controls: ['baseline', 'ablation', 'sanity_check'],
      rationale: 'The Scientist refuses to reduce scope enough to become feasible.',
    },
    4: {
      sample_size: 72,
      controls: ['baseline', 'ablation', 'sanity_check'],
      rationale: 'The protocol remains too expensive and staff-heavy for this lab.',
    },
    5: {
      sample_size: 68,
      controls: ['baseline', 'ablation', 'sanity_check'],
      rationale: 'Final round: still no viable path to agreement under the current constraints.',
    },
  };

  return buildScenarioAwareProposal(state, {
    technique: defaultTechnique,
    duration_days: Math.min(4, state.lab_constraints.time_limit_days),
    required_equipment: defaultEquipment,
    required_reagents: defaultReagents,
    ...(rejectionPlan[state.round] ?? rejectionPlan[5]),
  });
}
