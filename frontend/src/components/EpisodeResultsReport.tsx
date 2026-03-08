import type { ReactNode } from 'react';
import {
  CheckCircle2,
  AlertTriangle,
  XCircle,
  BrainCircuit,
  TrendingUp,
  Wrench,
  Gauge,
  FileCheck2,
} from 'lucide-react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  BarChart,
  Bar,
} from 'recharts';
import type { EpisodeState } from '@/types';
import { cn, formatReward } from '@/lib/utils';

interface EpisodeResultsReportProps {
  episode: EpisodeState;
  className?: string;
}

type OutcomeProfile = {
  tone: 'good' | 'learning' | 'reject';
  title: string;
  subtitle: string;
  badge: string;
  icon: typeof CheckCircle2;
};

const TOOL_STACK: Record<string, { title: string; packages: string[]; commands: string[] }> = {
  math_reasoning: {
    title: 'Suggested proof-and-verification stack',
    packages: ['SymPy', 'pytest', 'JupyterLab', 'LaTeX tooling'],
    commands: [
      'pip install sympy pytest jupyterlab',
      'Install TeX distribution for reproducible proof write-ups',
    ],
  },
  ml_benchmark: {
    title: 'Suggested replication toolchain',
    packages: ['PyTorch', 'torchvision', 'Weights & Biases', 'datasets'],
    commands: [
      'pip install torch torchvision wandb datasets',
      'Install NVIDIA CUDA toolkit / drivers that match the available GPU node',
    ],
  },
  finance_trading: {
    title: 'Suggested backtest stack',
    packages: ['pandas', 'numpy', 'vectorbt', 'matplotlib'],
    commands: [
      'pip install pandas numpy vectorbt matplotlib',
      'Add a versioned market-data export before rerunning the benchmark',
    ],
  },
};

function computeConfidencePercent(episode: EpisodeState): number {
  const scores = episode.scores;
  if (!scores) {
    return 0;
  }

  const weighted =
    scores.rigor * 0.4 +
    scores.feasibility * 0.35 +
    scores.fidelity * 0.25;
  return Math.round(weighted * 100);
}

function buildReliabilityLabel(episode: EpisodeState): string {
  if (episode.judge_audit?.verdict === 'accept' && episode.step_history[0]?.lab_manager_action_type === 'accept') {
    return 'Good';
  }
  if (episode.judge_audit?.verdict === 'accept') {
    return 'Needs iteration';
  }
  return 'Bad';
}

function buildOutcomeProfile(episode: EpisodeState): OutcomeProfile {
  const firstRoundAccepted =
    episode.step_history[0]?.lab_manager_action_type === 'accept' &&
    episode.judge_audit?.verdict === 'accept';
  const disagreementRounds = episode.step_history.filter(
    (trace) => trace.lab_manager_action_type && trace.lab_manager_action_type !== 'accept',
  ).length;

  if (firstRoundAccepted) {
    return {
      tone: 'good',
      title: 'Completed: First-round agreement',
      subtitle: 'The paper looks replicable under the current constraints, and the agents converged immediately.',
      badge: 'Good paper / strong replication candidate',
      icon: CheckCircle2,
    };
  }

  if (episode.judge_audit?.verdict === 'accept') {
    return {
      tone: 'learning',
      title: 'Completed: Multi-round learning opportunity',
      subtitle: `${disagreementRounds} disagreement round(s) were resolved into a feasible final protocol.`,
      badge: 'Heavy RL learning opportunity',
      icon: AlertTriangle,
    };
  }

  return {
    tone: 'reject',
    title: 'Completed: No agreement reached',
    subtitle: 'The protocol never became acceptable within the six-round limit, so the paper is rejected for this lab setup.',
    badge: 'Cannot replicate under current setup',
    icon: XCircle,
  };
}

function aggregateRewardComponents(episode: EpisodeState): Array<{ key: string; value: number }> {
  const totals = new Map<string, number>();
  for (const trace of episode.step_history) {
    for (const [key, value] of Object.entries(trace.step_reward_components)) {
      totals.set(key, (totals.get(key) ?? 0) + value);
    }
  }

  return [...totals.entries()]
    .map(([key, value]) => ({ key, value: Number(value.toFixed(3)) }))
    .sort((a, b) => Math.abs(b.value) - Math.abs(a.value));
}

function buildLearningBullets(episode: EpisodeState): string[] {
  const firstProtocol = episode.step_history.find((trace) => trace.protocol)?.protocol;
  const finalProtocol = episode.protocol;
  const bullets: string[] = [];

  if (firstProtocol && finalProtocol && firstProtocol.sample_size !== finalProtocol.sample_size) {
    bullets.push(
      `Sample size moved from ${firstProtocol.sample_size} to ${finalProtocol.sample_size}, showing explicit adaptation to budget or staff feedback.`,
    );
  }

  if (firstProtocol && finalProtocol && firstProtocol.controls.length !== finalProtocol.controls.length) {
    bullets.push(
      `Controls were narrowed from ${firstProtocol.controls.length} to ${finalProtocol.controls.length}, which reduced lab pressure while preserving the core benchmark check.`,
    );
  }

  if (episode.step_history.some((trace) => trace.lab_manager_action_type === 'suggest_alternative')) {
    bullets.push('The Scientist absorbed grounded Lab Manager alternatives instead of ignoring the resource constraints.');
  }

  if (episode.step_history.some((trace) => trace.step_reward_components.momentum_bonus)) {
    bullets.push('Later revisions earned momentum bonuses, meaning the protocol improved rather than stalling.');
  }

  if (!bullets.length) {
    bullets.push('The episode converged quickly, so the strongest training value is as a positive exemplar for future rollouts.');
  }

  return bullets;
}

function buildImprovementBullets(episode: EpisodeState): string[] {
  const scores = episode.scores;
  const verdict = episode.judge_audit?.verdict ?? 'unknown';
  const suggestions: string[] = [];

  if (!scores) {
    suggestions.push('Provision more compute, staff, or schedule slack before attempting another replication run.');
    suggestions.push('Reduce sample size and control scope earlier to avoid spending the full round budget on infeasible plans.');
    return suggestions;
  }

  if (scores.rigor < 0.7) {
    suggestions.push('Improve rigor by tightening success criteria, controls, and evaluation checkpoints in the proposed protocol.');
  }
  if (scores.feasibility < 0.9) {
    suggestions.push('Improve feasibility by reducing workload earlier or aligning the protocol more closely with the available staff and equipment.');
  }
  if (scores.fidelity < 0.7) {
    suggestions.push('Improve fidelity by matching the original method and baseline recipe more closely.');
  }
  if (verdict !== 'accept') {
    suggestions.push('Use this rollout as a negative exemplar in RL training so the Scientist learns to avoid repeated non-feasible plans.');
  }
  if (!suggestions.length) {
    suggestions.push('This is a strong positive exemplar; the next improvement is broader held-out evaluation rather than protocol repair.');
  }

  return suggestions;
}

export default function EpisodeResultsReport({ episode, className }: EpisodeResultsReportProps) {
  const profile = buildOutcomeProfile(episode);
  const confidencePercent = computeConfidencePercent(episode);
  const reliabilityLabel = buildReliabilityLabel(episode);
  const disagreementRounds = episode.step_history.filter(
    (trace) => trace.lab_manager_action_type && trace.lab_manager_action_type !== 'accept',
  ).length;
  const chartData = episode.step_history.map((trace) => ({
    round: `R${trace.round}`,
    reward: Number(trace.reward.toFixed(3)),
    cumulative: Number(trace.cumulative_reward.toFixed(3)),
  }));
  const scoreBars = [
    { key: 'rigor', value: episode.scores?.rigor ?? 0 },
    { key: 'feasibility', value: episode.scores?.feasibility ?? 0 },
    { key: 'fidelity', value: episode.scores?.fidelity ?? 0 },
    { key: 'parsimony', value: episode.scores?.parsimony ?? 0 },
  ];
  const rewardComponents = aggregateRewardComponents(episode);
  const toolStack = TOOL_STACK[episode.template];
  const ProfileIcon = profile.icon;

  return (
    <section className={cn('rounded-2xl border border-border bg-card p-6', className)}>
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <div
            className={cn(
              'mb-3 inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-semibold',
              profile.tone === 'good' && 'bg-lab-manager/10 text-lab-manager',
              profile.tone === 'learning' && 'bg-judge/10 text-judge',
              profile.tone === 'reject' && 'bg-destructive/10 text-destructive',
            )}
          >
            <ProfileIcon className="h-4 w-4" />
            {profile.badge}
          </div>
          <h2 className="text-2xl font-bold">{profile.title}</h2>
          <p className="mt-2 max-w-3xl text-sm text-muted-foreground">{profile.subtitle}</p>
          <p className="mt-3 max-w-3xl text-sm">
            {profile.tone !== 'reject'
              ? `ReplicaLab scores this paper as replicable in the current lab setup with ${confidencePercent}% confidence.`
              : `ReplicaLab rejects this paper for the current setup. The paper reliability score is ${confidencePercent}% until the blocking constraints are addressed.`}
          </p>
        </div>

        <div className="grid gap-3 sm:grid-cols-2 lg:w-[360px]">
          <MetricCard
            icon={<Gauge className="h-4 w-4" />}
            label="Replicability score"
            value={`${confidencePercent}%`}
            hint="Derived from rigor, feasibility, and fidelity."
          />
          <MetricCard
            icon={<CheckCircle2 className="h-4 w-4" />}
            label="Paper reliability quality"
            value={reliabilityLabel}
            hint="Good, learning opportunity, or bad based on the judged outcome."
          />
          <MetricCard
            icon={<FileCheck2 className="h-4 w-4" />}
            label="Judge verdict"
            value={episode.judge_audit?.verdict ?? 'unknown'}
            hint="Canonical deterministic decision."
          />
          <MetricCard
            icon={<TrendingUp className="h-4 w-4" />}
            label="Total reward"
            value={formatReward(episode.cumulative_reward)}
            hint={`Cumulative reward across ${episode.step_history.length} executed round(s).`}
          />
        </div>
      </div>

      <div className="mt-4 rounded-xl border border-border bg-muted/30 p-4">
        <div className="flex flex-wrap items-center gap-2 text-xs font-medium">
          <span className="rounded-full bg-background px-2.5 py-1 text-primary">
            Executed rounds: {episode.step_history.length} / {episode.max_rounds}
          </span>
          <span className="rounded-full bg-background px-2.5 py-1 text-primary">
            Disagreement rounds: {disagreementRounds}
          </span>
          <span className="rounded-full bg-background px-2.5 py-1 text-primary">
            Final status: {episode.done ? 'completed' : 'in progress'}
          </span>
        </div>
      </div>

      <div className="mt-6 grid gap-4 xl:grid-cols-2">
        <div className="rounded-xl border border-border bg-muted/30 p-4">
          <h3 className="mb-2 text-sm font-semibold">Round-by-round reward trajectory</h3>
          <p className="mb-4 text-xs text-muted-foreground">
            This is real episode data from the run you just watched, not static demo text.
          </p>
          <div className="h-60">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                <XAxis dataKey="round" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Legend wrapperStyle={{ fontSize: '12px' }} />
                <Line type="monotone" dataKey="reward" stroke="var(--color-primary)" strokeWidth={2.5} name="Step reward" />
                <Line type="monotone" dataKey="cumulative" stroke="var(--color-lab-manager)" strokeWidth={2.5} name="Cumulative reward" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="rounded-xl border border-border bg-muted/30 p-4">
          <h3 className="mb-2 text-sm font-semibold">Terminal score profile</h3>
          <p className="mb-4 text-xs text-muted-foreground">
            The final verdict depends on these component scores plus the terminal rubric.
          </p>
          <div className="h-60">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={scoreBars}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                <XAxis dataKey="key" tick={{ fontSize: 11 }} />
                <YAxis domain={[0, 1]} tickFormatter={(value) => `${Math.round(value * 100)}%`} tick={{ fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="value" fill="var(--color-judge)" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="mt-6 grid gap-4 xl:grid-cols-3">
        <InsightCard
          title="What the agents learned"
          icon={<BrainCircuit className="h-4 w-4" />}
          items={buildLearningBullets(episode)}
        />
        <InsightCard
          title="What to improve next"
          icon={<TrendingUp className="h-4 w-4" />}
          items={buildImprovementBullets(episode)}
        />
        <InsightCard
          title="Next tools to install"
          icon={<Wrench className="h-4 w-4" />}
          items={[
            toolStack.title,
            ...toolStack.packages.map((item) => `Install ${item}`),
            ...toolStack.commands,
          ]}
        />
      </div>

      <div className="mt-6 grid gap-4 xl:grid-cols-[1.5fr_1fr]">
        <div className="rounded-xl border border-border bg-muted/30 p-4">
          <h3 className="mb-3 text-sm font-semibold">Episode timeline</h3>
          <div className="space-y-3">
            {episode.step_history.map((trace) => (
              <div key={trace.round} className="rounded-lg border border-border bg-background p-3">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="rounded-full bg-primary/10 px-2 py-0.5 text-[11px] font-semibold text-primary">
                    Round {trace.round}
                  </span>
                  <span className="rounded-full bg-muted px-2 py-0.5 text-[11px] text-muted-foreground">
                    Scientist: {trace.action_type.replace(/_/g, ' ')}
                  </span>
                  {trace.lab_manager_action_type && (
                    <span className="rounded-full bg-muted px-2 py-0.5 text-[11px] text-muted-foreground">
                      Lab Manager: {trace.lab_manager_action_type.replace(/_/g, ' ')}
                    </span>
                  )}
                  <span className="ml-auto text-xs font-semibold text-foreground">
                    {formatReward(trace.reward)}
                  </span>
                </div>
                <p className="mt-2 text-xs text-muted-foreground">{trace.scientist_message}</p>
                {trace.lab_manager_message && (
                  <p className="mt-1 text-xs text-muted-foreground">{trace.lab_manager_message}</p>
                )}
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-xl border border-border bg-muted/30 p-4">
          <h3 className="mb-3 text-sm font-semibold">Reward component ledger</h3>
          <div className="space-y-2">
            {rewardComponents.length ? rewardComponents.map((entry) => (
              <div key={entry.key} className="flex items-center justify-between rounded-lg border border-border bg-background px-3 py-2 text-xs">
                <span className="capitalize text-muted-foreground">{entry.key.replace(/_/g, ' ')}</span>
                <span className={cn('font-semibold', entry.value >= 0 ? 'text-lab-manager' : 'text-destructive')}>
                  {entry.value >= 0 ? '+' : ''}
                  {entry.value.toFixed(3)}
                </span>
              </div>
            )) : (
              <div className="rounded-lg border border-border bg-background px-3 py-2 text-xs text-muted-foreground">
                No intermediate reward components were emitted in this episode.
              </div>
            )}
          </div>

          <div className="mt-4 rounded-lg border border-border bg-background p-3">
            <div className="mb-2 text-xs font-semibold">Training interpretation</div>
            <p className="text-xs text-muted-foreground">
              {profile.tone === 'good' &&
                'Use this run as a positive exemplar: the policy found a feasible replication plan with minimal negotiation overhead.'}
              {profile.tone === 'learning' &&
                'This is the richest RL case: multiple disagreement rounds created dense reward signals for the Scientist to learn from.'}
              {profile.tone === 'reject' &&
                'This is a strong negative exemplar: the policy spent all six rounds without resolving the key feasibility blockers.'}
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}

function MetricCard({
  icon,
  label,
  value,
  hint,
}: {
  icon: ReactNode;
  label: string;
  value: string;
  hint: string;
}) {
  return (
    <div className="rounded-xl border border-border bg-muted/30 p-3">
      <div className="mb-2 flex items-center gap-2 text-xs text-muted-foreground">
        {icon}
        {label}
      </div>
      <div className="text-lg font-bold">{value}</div>
      <p className="mt-1 text-[11px] text-muted-foreground">{hint}</p>
    </div>
  );
}

function InsightCard({
  title,
  icon,
  items,
}: {
  title: string;
  icon: ReactNode;
  items: string[];
}) {
  return (
    <div className="rounded-xl border border-border bg-muted/30 p-4">
      <div className="mb-3 flex items-center gap-2 text-sm font-semibold">
        {icon}
        {title}
      </div>
      <div className="space-y-2">
        {items.map((item) => (
          <div key={item} className="rounded-lg border border-border bg-background px-3 py-2 text-xs text-muted-foreground">
            {item}
          </div>
        ))}
      </div>
    </div>
  );
}
