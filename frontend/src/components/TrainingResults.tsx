import { useState } from 'react';
import { TrendingUp, BarChart3, ToggleLeft, ToggleRight } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import type { TrainingComparison } from '@/types';
import { cn, formatReward, formatScore } from '@/lib/utils';

interface TrainingResultsProps {
  data?: TrainingComparison;
  className?: string;
}

const MOCK_COMPARISON: TrainingComparison = {
  baseline: Array.from({ length: 20 }, (_, i) => ({
    episode: i + 1, reward: 3.5 + Math.random() * 1.5, rigor: 0.5 + Math.random() * 0.2,
    feasibility: 0.4 + Math.random() * 0.25, fidelity: 0.55 + Math.random() * 0.15,
    rounds_used: Math.floor(3 + Math.random() * 2), agreement: Math.random() > 0.5, invalid_actions: Math.floor(Math.random() * 3),
  })),
  trained: Array.from({ length: 20 }, (_, i) => ({
    episode: i + 1, reward: 4.5 + Math.min(i * 0.15, 3) + Math.random() * 1,
    rigor: 0.6 + Math.min(i * 0.01, 0.2) + Math.random() * 0.1, feasibility: 0.55 + Math.min(i * 0.015, 0.25) + Math.random() * 0.1,
    fidelity: 0.6 + Math.min(i * 0.01, 0.2) + Math.random() * 0.1,
    rounds_used: Math.max(2, Math.floor(4 - i * 0.05 + Math.random())), agreement: Math.random() > 0.3,
    invalid_actions: Math.max(0, Math.floor(2 - i * 0.1 + Math.random())),
  })),
  summary: {
    baseline_avg_reward: 4.25, trained_avg_reward: 7.1, baseline_agreement_rate: 0.5,
    trained_agreement_rate: 0.8, baseline_avg_rounds: 4.1, trained_avg_rounds: 2.8,
    baseline_invalid_rate: 0.15, trained_invalid_rate: 0.04,
  },
};

export default function TrainingResults({ data, className }: TrainingResultsProps) {
  const comparison = data ?? MOCK_COMPARISON;
  const [showTrained, setShowTrained] = useState(true);
  const chartData = comparison.baseline.map((b, i) => ({
    episode: b.episode, baseline: parseFloat(b.reward.toFixed(2)),
    trained: parseFloat(comparison.trained[i]?.reward.toFixed(2) ?? '0'),
  }));
  const s = comparison.summary;

  return (
    <div className={cn('rounded-lg border border-border bg-card p-4', className)}>
      <div className="mb-4 flex items-center gap-2">
        <TrendingUp className="h-4 w-4 text-primary" />
        <h2 className="text-sm font-semibold">Training Results</h2>
        <button onClick={() => setShowTrained(!showTrained)}
          className="ml-auto flex items-center gap-1.5 rounded-md border border-border px-2 py-1 text-xs transition-colors hover:bg-muted">
          {showTrained ? <ToggleRight className="h-4 w-4 text-primary" /> : <ToggleLeft className="h-4 w-4 text-muted-foreground" />}
          {showTrained ? 'Trained' : 'Baseline'}
        </button>
      </div>
      <div className="mb-4 h-48">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--color-chart-grid)" />
            <XAxis dataKey="episode" tick={{ fontSize: 10, fill: 'var(--color-chart-text)' }} />
            <YAxis tick={{ fontSize: 10, fill: 'var(--color-chart-text)' }} />
            <Tooltip contentStyle={{ backgroundColor: 'var(--color-card)', border: '1px solid var(--color-border)', borderRadius: '0.375rem', fontSize: '12px' }} />
            <Legend wrapperStyle={{ fontSize: '11px' }} />
            <Line type="monotone" dataKey="baseline" stroke="var(--color-chart-muted)" strokeWidth={1.5} dot={false} name="Baseline" />
            {showTrained && <Line type="monotone" dataKey="trained" stroke="var(--color-primary)" strokeWidth={2} dot={false} name="Trained" />}
          </LineChart>
        </ResponsiveContainer>
      </div>
      <div className="grid grid-cols-2 gap-2">
        <MetricCard icon={<BarChart3 className="h-3.5 w-3.5" />} label="Avg Reward" baseline={formatReward(s.baseline_avg_reward)} trained={formatReward(s.trained_avg_reward)} improved={s.trained_avg_reward > s.baseline_avg_reward} />
        <MetricCard icon={<BarChart3 className="h-3.5 w-3.5" />} label="Agreement" baseline={formatScore(s.baseline_agreement_rate)} trained={formatScore(s.trained_agreement_rate)} improved={s.trained_agreement_rate > s.baseline_agreement_rate} />
        <MetricCard icon={<BarChart3 className="h-3.5 w-3.5" />} label="Avg Rounds" baseline={s.baseline_avg_rounds.toFixed(1)} trained={s.trained_avg_rounds.toFixed(1)} improved={s.trained_avg_rounds < s.baseline_avg_rounds} />
        <MetricCard icon={<BarChart3 className="h-3.5 w-3.5" />} label="Invalid Rate" baseline={formatScore(s.baseline_invalid_rate)} trained={formatScore(s.trained_invalid_rate)} improved={s.trained_invalid_rate < s.baseline_invalid_rate} />
      </div>
    </div>
  );
}

function MetricCard({ icon, label, baseline, trained, improved }: { icon: React.ReactNode; label: string; baseline: string; trained: string; improved: boolean }) {
  return (
    <div className="rounded-md bg-muted/50 p-2">
      <div className="mb-1 flex items-center gap-1 text-xs text-muted-foreground">{icon}{label}</div>
      <div className="flex items-baseline gap-2 text-xs">
        <span className="text-muted-foreground">{baseline}</span>
        <span className="text-muted-foreground">\u2192</span>
        <span className={cn('font-semibold', improved ? 'text-lab-manager' : 'text-destructive')}>{trained}</span>
      </div>
    </div>
  );
}
