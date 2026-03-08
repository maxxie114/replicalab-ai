import { useState, type ReactNode } from 'react';
import {
  TrendingUp,
  BarChart3,
  ToggleLeft,
  ToggleRight,
  FileText,
  Cpu,
  FlaskConical,
  Scale,
} from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import type { TrainingComparison } from '@/types';
import { cn, formatReward, formatScore } from '@/lib/utils';

interface TrainingResultsProps {
  data?: TrainingComparison;
  className?: string;
}

const DEMO_COMPARISON: TrainingComparison = {
  baseline: [
    { episode: 1, reward: 3.8, rigor: 0.58, feasibility: 0.46, fidelity: 0.55, rounds_used: 5, agreement: false, invalid_actions: 2 },
    { episode: 2, reward: 4.0, rigor: 0.6, feasibility: 0.48, fidelity: 0.56, rounds_used: 5, agreement: false, invalid_actions: 2 },
    { episode: 3, reward: 4.1, rigor: 0.61, feasibility: 0.5, fidelity: 0.57, rounds_used: 5, agreement: true, invalid_actions: 1 },
    { episode: 4, reward: 4.2, rigor: 0.62, feasibility: 0.5, fidelity: 0.58, rounds_used: 4, agreement: true, invalid_actions: 1 },
    { episode: 5, reward: 4.0, rigor: 0.6, feasibility: 0.49, fidelity: 0.58, rounds_used: 5, agreement: false, invalid_actions: 2 },
    { episode: 6, reward: 4.3, rigor: 0.63, feasibility: 0.52, fidelity: 0.59, rounds_used: 4, agreement: true, invalid_actions: 1 },
    { episode: 7, reward: 4.1, rigor: 0.61, feasibility: 0.5, fidelity: 0.58, rounds_used: 5, agreement: false, invalid_actions: 2 },
    { episode: 8, reward: 4.4, rigor: 0.64, feasibility: 0.53, fidelity: 0.6, rounds_used: 4, agreement: true, invalid_actions: 1 },
    { episode: 9, reward: 4.2, rigor: 0.62, feasibility: 0.51, fidelity: 0.59, rounds_used: 4, agreement: true, invalid_actions: 1 },
    { episode: 10, reward: 4.0, rigor: 0.6, feasibility: 0.48, fidelity: 0.57, rounds_used: 5, agreement: false, invalid_actions: 2 },
    { episode: 11, reward: 4.3, rigor: 0.64, feasibility: 0.52, fidelity: 0.6, rounds_used: 4, agreement: true, invalid_actions: 1 },
    { episode: 12, reward: 4.1, rigor: 0.61, feasibility: 0.49, fidelity: 0.58, rounds_used: 5, agreement: false, invalid_actions: 2 },
  ],
  trained: [
    { episode: 1, reward: 4.5, rigor: 0.64, feasibility: 0.56, fidelity: 0.6, rounds_used: 4, agreement: true, invalid_actions: 1 },
    { episode: 2, reward: 4.8, rigor: 0.67, feasibility: 0.58, fidelity: 0.62, rounds_used: 4, agreement: true, invalid_actions: 1 },
    { episode: 3, reward: 5.0, rigor: 0.69, feasibility: 0.61, fidelity: 0.64, rounds_used: 4, agreement: true, invalid_actions: 1 },
    { episode: 4, reward: 5.2, rigor: 0.71, feasibility: 0.63, fidelity: 0.66, rounds_used: 3, agreement: true, invalid_actions: 1 },
    { episode: 5, reward: 5.5, rigor: 0.73, feasibility: 0.66, fidelity: 0.68, rounds_used: 3, agreement: true, invalid_actions: 0 },
    { episode: 6, reward: 5.7, rigor: 0.75, feasibility: 0.68, fidelity: 0.69, rounds_used: 3, agreement: true, invalid_actions: 0 },
    { episode: 7, reward: 5.9, rigor: 0.76, feasibility: 0.7, fidelity: 0.7, rounds_used: 3, agreement: true, invalid_actions: 0 },
    { episode: 8, reward: 6.1, rigor: 0.78, feasibility: 0.72, fidelity: 0.72, rounds_used: 3, agreement: true, invalid_actions: 0 },
    { episode: 9, reward: 6.3, rigor: 0.79, feasibility: 0.74, fidelity: 0.73, rounds_used: 3, agreement: true, invalid_actions: 0 },
    { episode: 10, reward: 6.5, rigor: 0.8, feasibility: 0.76, fidelity: 0.75, rounds_used: 3, agreement: true, invalid_actions: 0 },
    { episode: 11, reward: 6.6, rigor: 0.81, feasibility: 0.77, fidelity: 0.76, rounds_used: 2, agreement: true, invalid_actions: 0 },
    { episode: 12, reward: 6.8, rigor: 0.83, feasibility: 0.79, fidelity: 0.78, rounds_used: 2, agreement: true, invalid_actions: 0 },
  ],
  summary: {
    baseline_avg_reward: 4.13,
    trained_avg_reward: 5.74,
    baseline_agreement_rate: 0.5,
    trained_agreement_rate: 0.92,
    baseline_avg_rounds: 4.58,
    trained_avg_rounds: 3.0,
    baseline_invalid_rate: 0.15,
    trained_invalid_rate: 0.03,
  },
};

export default function TrainingResults({ data, className }: TrainingResultsProps) {
  const comparison = data ?? DEMO_COMPARISON;
  const [showTrained, setShowTrained] = useState(true);
  const chartData = comparison.baseline.map((baselinePoint, index) => ({
    episode: baselinePoint.episode,
    baseline: Number(baselinePoint.reward.toFixed(2)),
    trained: Number((comparison.trained[index]?.reward ?? 0).toFixed(2)),
  }));
  const summary = comparison.summary;

  return (
    <div className={cn('rounded-lg border border-border bg-card p-4', className)}>
      <div className="mb-4 flex items-center gap-2">
        <TrendingUp className="h-4 w-4 text-primary" />
        <h2 className="text-sm font-semibold">Training Story</h2>
        <button
          onClick={() => setShowTrained((value) => !value)}
          className="ml-auto flex items-center gap-1.5 rounded-md border border-border px-2 py-1 text-xs transition-colors hover:bg-muted"
        >
          {showTrained ? <ToggleRight className="h-4 w-4 text-primary" /> : <ToggleLeft className="h-4 w-4 text-muted-foreground" />}
          {showTrained ? 'Highlight trained' : 'Highlight baseline'}
        </button>
      </div>

      <div className="mb-4 flex flex-wrap gap-2">
        <span className="rounded-full bg-primary/10 px-2 py-1 text-[11px] font-medium text-primary">Minimal Colab notebook</span>
        <span className="rounded-full bg-scientist/10 px-2 py-1 text-[11px] font-medium text-scientist">Unsloth + HF TRL</span>
        <span className="rounded-full bg-judge/10 px-2 py-1 text-[11px] font-medium text-judge">Deterministic judge reward</span>
      </div>

      <p className="mb-4 text-sm text-muted-foreground">
        The same seeded replication tasks are used for baseline and trained runs. The Scientist only improves if it
        can negotiate stronger protocols under the exact same judge rubric.
      </p>

      <div className="mb-4 grid gap-2 sm:grid-cols-2 xl:grid-cols-4">
        <StoryCard icon={<FileText className="h-3.5 w-3.5" />} title="Notebook" detail="`train_minimal_colab.ipynb` is the sponsor-facing minimal GRPO path." />
        <StoryCard icon={<Cpu className="h-3.5 w-3.5" />} title="Trainer" detail="Unsloth + TRL update the Scientist LoRA adapter on seeded tasks." />
        <StoryCard icon={<FlaskConical className="h-3.5 w-3.5" />} title="Environment" detail="Episodes come from the same paper-derived ReplicaLab benchmark families." />
        <StoryCard icon={<Scale className="h-3.5 w-3.5" />} title="Reward" detail="Rigor, feasibility, and fidelity stay deterministic for clean comparisons." />
      </div>

      <div className="mb-4 h-48">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--color-chart-grid)" />
            <XAxis dataKey="episode" tick={{ fontSize: 10, fill: 'var(--color-chart-text)' }} />
            <YAxis tick={{ fontSize: 10, fill: 'var(--color-chart-text)' }} />
            <Tooltip
              contentStyle={{
                backgroundColor: 'var(--color-card)',
                border: '1px solid var(--color-border)',
                borderRadius: '0.375rem',
                fontSize: '12px',
              }}
            />
            <Legend wrapperStyle={{ fontSize: '11px' }} />
            <Line
              type="monotone"
              dataKey="baseline"
              stroke="var(--color-chart-muted)"
              strokeOpacity={showTrained ? 0.35 : 1}
              strokeWidth={showTrained ? 1.5 : 2.5}
              dot={false}
              name="Baseline"
            />
            <Line
              type="monotone"
              dataKey="trained"
              stroke="var(--color-primary)"
              strokeOpacity={showTrained ? 1 : 0.35}
              strokeWidth={showTrained ? 2.5 : 1.5}
              dot={false}
              name="Trained"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-2 gap-2">
        <MetricCard icon={<BarChart3 className="h-3.5 w-3.5" />} label="Avg Reward" baseline={formatReward(summary.baseline_avg_reward)} trained={formatReward(summary.trained_avg_reward)} improved={summary.trained_avg_reward > summary.baseline_avg_reward} />
        <MetricCard icon={<BarChart3 className="h-3.5 w-3.5" />} label="Agreement" baseline={formatScore(summary.baseline_agreement_rate)} trained={formatScore(summary.trained_agreement_rate)} improved={summary.trained_agreement_rate > summary.baseline_agreement_rate} />
        <MetricCard icon={<BarChart3 className="h-3.5 w-3.5" />} label="Avg Rounds" baseline={summary.baseline_avg_rounds.toFixed(1)} trained={summary.trained_avg_rounds.toFixed(1)} improved={summary.trained_avg_rounds < summary.baseline_avg_rounds} />
        <MetricCard icon={<BarChart3 className="h-3.5 w-3.5" />} label="Invalid Rate" baseline={formatScore(summary.baseline_invalid_rate)} trained={formatScore(summary.trained_invalid_rate)} improved={summary.trained_invalid_rate < summary.baseline_invalid_rate} />
      </div>

      <p className="mt-4 text-xs text-muted-foreground">
        This packaged panel is the demo view for fixed-seed training metrics. When live run artifacts are wired in,
        the same layout can render real summary JSON from the training outputs.
      </p>
    </div>
  );
}

function StoryCard({ icon, title, detail }: { icon: ReactNode; title: string; detail: string }) {
  return (
    <div className="rounded-md border border-border bg-muted/40 p-3">
      <div className="mb-1 flex items-center gap-1.5 text-xs font-semibold text-foreground">
        {icon}
        {title}
      </div>
      <p className="text-xs text-muted-foreground">{detail}</p>
    </div>
  );
}

function MetricCard({
  icon,
  label,
  baseline,
  trained,
  improved,
}: {
  icon: ReactNode;
  label: string;
  baseline: string;
  trained: string;
  improved: boolean;
}) {
  return (
    <div className="rounded-md bg-muted/50 p-2">
      <div className="mb-1 flex items-center gap-1 text-xs text-muted-foreground">
        {icon}
        {label}
      </div>
      <div className="flex items-baseline gap-2 text-xs">
        <span className="text-muted-foreground">{baseline}</span>
        <span className="text-muted-foreground">-&gt;</span>
        <span className={cn('font-semibold', improved ? 'text-lab-manager' : 'text-destructive')}>{trained}</span>
      </div>
    </div>
  );
}
