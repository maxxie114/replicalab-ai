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
import { HOLDOUT_COMPARE, LIVE_CHECKPOINTS, TRAINING_ASSESSMENT } from '@/data/trainingArtifacts';
import { cn, formatReward, formatScore } from '@/lib/utils';

interface TrainingResultsProps {
  data?: TrainingComparison;
  className?: string;
}

export default function TrainingResults({ data, className }: TrainingResultsProps) {
  const comparison = data ?? HOLDOUT_COMPARE;
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
        <span className="rounded-full bg-destructive/10 px-2 py-1 text-[11px] font-medium text-destructive">
          More training required
        </span>
      </div>

      <p className="mb-4 text-sm text-muted-foreground">
        This panel now uses the real hold-out compare artifact. The training stack ran successfully, but the current
        trained Scientist still underperforms the deterministic baseline on fixed seeded evaluation.
      </p>

      <div className="mb-4 grid gap-2 sm:grid-cols-2 xl:grid-cols-4">
        <StoryCard icon={<FileText className="h-3.5 w-3.5" />} title="Notebook" detail="`train_minimal_colab.ipynb` is the sponsor-facing minimal GRPO path." />
        <StoryCard icon={<Cpu className="h-3.5 w-3.5" />} title="Trainer" detail="Unsloth + TRL update the Scientist LoRA adapter on seeded tasks." />
        <StoryCard icon={<FlaskConical className="h-3.5 w-3.5" />} title="Environment" detail="Episodes come from the same paper-derived ReplicaLab benchmark families." />
        <StoryCard icon={<Scale className="h-3.5 w-3.5" />} title="Reward" detail={`Latest live checkpoint reached ${formatReward(LIVE_CHECKPOINTS[LIVE_CHECKPOINTS.length - 1].averageReward)} average reward at ${(LIVE_CHECKPOINTS[LIVE_CHECKPOINTS.length - 1].agreementRate * 100).toFixed(0)}% agreement.`} />
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
        Current status: {TRAINING_ASSESSMENT.achieved[2]} The next gate is reducing invalid actions and rerunning
        the hold-out compare until trained performance overtakes baseline.
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
