import { useEffect, useState } from 'react';
import { Play, RotateCcw, Dices } from 'lucide-react';
import type { Difficulty, ScenarioTemplate, ResetParams } from '@/types';
import { cn } from '@/lib/utils';
import { sfx } from '@/lib/audio';
import { healthCheck } from '@/lib/api';

const TEMPLATES: { value: ScenarioTemplate; label: string }[] = [
  { value: 'math_reasoning', label: 'Math Reasoning' },
  { value: 'ml_benchmark', label: 'ML Benchmark' },
  { value: 'finance_trading', label: 'Finance Trading' },
];

const DIFFICULTIES: { value: Difficulty; label: string }[] = [
  { value: 'easy', label: 'Easy' },
  { value: 'medium', label: 'Medium' },
  { value: 'hard', label: 'Hard' },
];

interface ControlsProps {
  onStart: (params: ResetParams) => void;
  onStep?: () => void;
  disabled?: boolean;
  episodeActive?: boolean;
  className?: string;
  initialSeed?: number;
  initialTemplate?: ScenarioTemplate;
  initialDifficulty?: Difficulty;
}

export default function Controls({
  onStart,
  onStep,
  disabled,
  episodeActive,
  className,
  initialSeed,
  initialTemplate,
  initialDifficulty,
}: ControlsProps) {
  const [seed, setSeed] = useState<string>(initialSeed?.toString() ?? '42');
  const [template, setTemplate] = useState<ScenarioTemplate>(initialTemplate ?? 'ml_benchmark');
  const [difficulty, setDifficulty] = useState<Difficulty>(initialDifficulty ?? 'medium');
  const [backendStatus, setBackendStatus] = useState<'checking' | 'ok' | 'error'>('checking');
  const [backendMessage, setBackendMessage] = useState<string>('Checking backend connection...');

  useEffect(() => {
    if (initialSeed !== undefined) {
      setSeed(initialSeed.toString());
    }
  }, [initialSeed]);

  useEffect(() => {
    if (initialTemplate) {
      setTemplate(initialTemplate);
    }
  }, [initialTemplate]);

  useEffect(() => {
    if (initialDifficulty) {
      setDifficulty(initialDifficulty);
    }
  }, [initialDifficulty]);

  useEffect(() => {
    let cancelled = false;

    async function checkBackend() {
      setBackendStatus('checking');
      setBackendMessage('Checking backend connection...');
      try {
        await healthCheck();
        if (!cancelled) {
          setBackendStatus('ok');
          setBackendMessage('Backend connected. The live environment is ready.');
        }
      } catch (error) {
        if (!cancelled) {
          const message = error instanceof Error ? error.message : 'Backend unavailable.';
          setBackendStatus('error');
          setBackendMessage(message);
        }
      }
    }

    void checkBackend();
    return () => {
      cancelled = true;
    };
  }, []);

  function randomSeed() { sfx.click(); setSeed(Math.floor(Math.random() * 10000).toString()); }
  function handleStart() { sfx.click(); onStart({ seed: seed ? parseInt(seed, 10) : undefined, template, difficulty }); }

  return (
    <div className={cn('rounded-lg border border-border bg-card p-4', className)}>
      <div className="mb-3">
        <h2 className="text-sm font-semibold">Replication Setup</h2>
        <p className="mt-1 text-xs text-muted-foreground">
          Choose the seeded paper-derived benchmark that becomes this negotiation environment.
        </p>
        <p
          className={cn(
            'mt-2 text-xs',
            backendStatus === 'ok' && 'text-emerald-600',
            backendStatus === 'checking' && 'text-muted-foreground',
            backendStatus === 'error' && 'text-destructive',
          )}
        >
          {backendMessage}
        </p>
      </div>
      <div className="space-y-3">
        <div>
          <label className="mb-1 block text-xs font-medium text-muted-foreground">Scenario Family</label>
          <select value={template} onChange={(e) => setTemplate(e.target.value as ScenarioTemplate)} disabled={disabled || episodeActive}
            className="w-full rounded-md border border-border bg-background px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-ring disabled:opacity-50">
            {TEMPLATES.map((t) => <option key={t.value} value={t.value}>{t.label}</option>)}
          </select>
        </div>
        <div>
          <label className="mb-1 block text-xs font-medium text-muted-foreground">Difficulty</label>
          <div className="flex gap-1">
            {DIFFICULTIES.map((d) => (
              <button key={d.value} onClick={() => { sfx.click(); setDifficulty(d.value); }} disabled={disabled || episodeActive}
                className={cn('flex-1 rounded-md border px-2 py-1.5 text-xs font-medium transition-colors',
                  difficulty === d.value ? 'border-primary bg-primary/10 text-primary' : 'border-border text-muted-foreground hover:bg-muted disabled:opacity-50')}>
                {d.label}
              </button>
            ))}
          </div>
        </div>
        <div>
          <label className="mb-1 block text-xs font-medium text-muted-foreground">Seeded Benchmark</label>
          <div className="flex gap-1.5">
            <input type="number" value={seed} onChange={(e) => setSeed(e.target.value)} disabled={disabled || episodeActive} placeholder="Random"
              className="w-full rounded-md border border-border bg-background px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-ring disabled:opacity-50" />
            <button onClick={randomSeed} disabled={disabled || episodeActive}
              className="rounded-md border border-border p-1.5 text-muted-foreground hover:bg-muted disabled:opacity-50" title="Random seed">
              <Dices className="h-4 w-4" />
            </button>
          </div>
        </div>
        <div className="flex gap-2 pt-1">
          <button onClick={handleStart} disabled={disabled}
            className={cn('flex flex-1 items-center justify-center gap-1.5 rounded-md px-3 py-2 text-sm font-medium transition-colors disabled:opacity-50',
              episodeActive ? 'border border-border text-muted-foreground hover:bg-muted' : 'bg-primary text-primary-foreground hover:bg-primary/90')}>
            {episodeActive ? (<><RotateCcw className="h-4 w-4" />Reset Episode</>) : (<><Play className="h-4 w-4" />Start Replication</>)}
          </button>
          {episodeActive && onStep && (
            <button onClick={onStep} disabled={disabled}
              className="flex items-center gap-1.5 rounded-md bg-scientist px-3 py-2 text-sm font-medium text-white transition-colors hover:bg-scientist/90 disabled:opacity-50">
              <Play className="h-4 w-4" />Advance Round
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
