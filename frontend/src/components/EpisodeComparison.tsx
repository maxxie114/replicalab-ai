import { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { GitCompareArrows, Play, Loader2 } from 'lucide-react';
import type { EpisodeState, ScenarioTemplate, Difficulty } from '@/types';
import { resetEpisode, stepEpisode, buildDefaultScientistAction, buildAcceptAction } from '@/lib/api';
import { cn, formatScore, formatReward } from '@/lib/utils';
import CharacterAvatar from '@/components/CharacterAvatar';

interface ComparisonRun {
  label: string;
  seed: number;
  difficulty: Difficulty;
  template: ScenarioTemplate;
  state: EpisodeState | null;
  status: 'idle' | 'running' | 'done' | 'error';
  error?: string;
}

export default function EpisodeComparison({ className }: { className?: string }) {
  const [runs, setRuns] = useState<ComparisonRun[]>([
    { label: 'Run A', seed: 42, difficulty: 'easy', template: 'math_reasoning', state: null, status: 'idle' },
    { label: 'Run B', seed: 42, difficulty: 'medium', template: 'math_reasoning', state: null, status: 'idle' },
    { label: 'Run C', seed: 42, difficulty: 'hard', template: 'math_reasoning', state: null, status: 'idle' },
  ]);
  const [running, setRunning] = useState(false);

  const updateRun = useCallback((index: number, patch: Partial<ComparisonRun>) => {
    setRuns((prev) => prev.map((r, i) => (i === index ? { ...r, ...patch } : r)));
  }, []);

  async function runSingleEpisode(index: number) {
    const run = runs[index];
    updateRun(index, { status: 'running', state: null, error: undefined });

    try {
      let state = await resetEpisode({
        seed: run.seed,
        template: run.template,
        difficulty: run.difficulty,
      });

      // Auto-play through all rounds
      while (!state.done) {
        const isLastRound = state.round >= state.max_rounds - 1;
        const action = isLastRound ? buildAcceptAction() : buildDefaultScientistAction();
        state = await stepEpisode(state.session_id, action, state);
      }

      updateRun(index, { state, status: 'done' });
    } catch (err) {
      updateRun(index, {
        status: 'error',
        error: err instanceof Error ? err.message : 'Unknown error',
      });
    }
  }

  async function runAll() {
    setRunning(true);
    await Promise.all(runs.map((_, i) => runSingleEpisode(i)));
    setRunning(false);
  }

  return (
    <div className={cn('rounded-xl border border-border bg-card p-6', className)}>
      <div className="mb-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <GitCompareArrows className="h-5 w-5 text-primary" />
          <h2 className="text-base font-bold">Episode Comparison</h2>
        </div>
        <button
          onClick={runAll}
          disabled={running}
          className="flex items-center gap-1.5 rounded-md bg-primary px-3 py-1.5 text-xs font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50 transition-colors"
        >
          {running ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Play className="h-3.5 w-3.5" />}
          Run All
        </button>
      </div>

      {/* Config rows */}
      <div className="mb-4 grid grid-cols-3 gap-3">
        {runs.map((run, i) => (
          <div key={i} className="rounded-lg border border-border p-3 space-y-2">
            <div className="flex items-center gap-1.5">
              <div className={cn(
                'h-2 w-2 rounded-full',
                run.status === 'done' ? 'bg-lab-manager' :
                run.status === 'running' ? 'bg-primary animate-pulse' :
                run.status === 'error' ? 'bg-destructive' : 'bg-muted-foreground',
              )} />
              <span className="text-xs font-bold">{run.label}</span>
            </div>
            <div className="space-y-1">
              <select
                value={run.template}
                onChange={(e) => updateRun(i, { template: e.target.value as ScenarioTemplate })}
                disabled={running}
                className="w-full rounded border border-border bg-background px-1.5 py-0.5 text-[10px]"
              >
                <option value="math_reasoning">Math Reasoning</option>
                <option value="ml_benchmark">ML Benchmark</option>
                <option value="finance_trading">Finance Trading</option>
              </select>
              <div className="flex gap-1">
                {(['easy', 'medium', 'hard'] as const).map((d) => (
                  <button
                    key={d}
                    onClick={() => updateRun(i, { difficulty: d })}
                    disabled={running}
                    className={cn(
                      'flex-1 rounded border px-1 py-0.5 text-[9px] font-medium transition-colors',
                      run.difficulty === d ? 'border-primary bg-primary/10 text-primary' : 'border-border text-muted-foreground',
                    )}
                  >
                    {d}
                  </button>
                ))}
              </div>
              <input
                type="number"
                value={run.seed}
                onChange={(e) => updateRun(i, { seed: parseInt(e.target.value) || 0 })}
                disabled={running}
                className="w-full rounded border border-border bg-background px-1.5 py-0.5 text-[10px]"
                placeholder="Seed"
              />
            </div>
          </div>
        ))}
      </div>

      {/* Results comparison */}
      <AnimatePresence>
        {runs.some((r) => r.status === 'done') && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <h3 className="mb-3 text-xs font-semibold text-muted-foreground">Results</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead>
                  <tr className="border-b border-border text-muted-foreground">
                    <th className="py-1.5 pr-3 text-left font-medium">Metric</th>
                    {runs.map((r, i) => (
                      <th key={i} className="py-1.5 px-3 text-center font-medium">{r.label}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {[
                    { label: 'Reward', fn: (s: EpisodeState) => formatReward(s.scores?.total_reward ?? 0) },
                    { label: 'Rigor', fn: (s: EpisodeState) => formatScore(s.scores?.rigor ?? 0) },
                    { label: 'Feasibility', fn: (s: EpisodeState) => formatScore(s.scores?.feasibility ?? 0) },
                    { label: 'Fidelity', fn: (s: EpisodeState) => formatScore(s.scores?.fidelity ?? 0) },
                    { label: 'Rounds', fn: (s: EpisodeState) => `${s.round}/${s.max_rounds}` },
                    { label: 'Verdict', fn: (s: EpisodeState) => s.judge_audit?.verdict ?? '-' },
                  ].map((metric) => (
                    <tr key={metric.label} className="border-b border-border/50">
                      <td className="py-1.5 pr-3 font-medium text-muted-foreground">{metric.label}</td>
                      {runs.map((r, i) => (
                        <td key={i} className="py-1.5 px-3 text-center">
                          {r.state ? (
                            <span className="font-medium">{metric.fn(r.state)}</span>
                          ) : r.status === 'running' ? (
                            <Loader2 className="inline h-3 w-3 animate-spin text-primary" />
                          ) : r.status === 'error' ? (
                            <span className="text-destructive">err</span>
                          ) : (
                            <span className="text-muted-foreground">-</span>
                          )}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Visual score bars comparison */}
            <div className="mt-4 space-y-2">
              {['rigor', 'feasibility', 'fidelity'].map((metric) => (
                <div key={metric}>
                  <div className="mb-1 text-[10px] font-medium capitalize text-muted-foreground">{metric}</div>
                  <div className="space-y-0.5">
                    {runs.map((r, i) => {
                      const val = r.state?.scores?.[metric as keyof typeof r.state.scores] as number | undefined;
                      return (
                        <div key={i} className="flex items-center gap-2">
                          <span className="w-10 text-[9px] font-medium">{r.label}</span>
                          <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-muted">
                            <motion.div
                              className={cn(
                                'h-full rounded-full',
                                metric === 'rigor' ? 'bg-scientist' : metric === 'feasibility' ? 'bg-lab-manager' : 'bg-judge',
                              )}
                              animate={{ width: `${(val ?? 0) * 100}%` }}
                              transition={{ duration: 0.5 }}
                            />
                          </div>
                          <span className="w-8 text-right text-[9px] font-bold">
                            {val !== undefined ? formatScore(val) : '-'}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
