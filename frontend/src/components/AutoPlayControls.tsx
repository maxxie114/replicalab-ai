import { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Play, Pause, FastForward, RotateCcw } from 'lucide-react';
import { cn } from '@/lib/utils';

interface AutoPlayControlsProps {
  isPlaying: boolean;
  speed: number;
  round: number;
  maxRounds: number;
  done: boolean;
  onTogglePlay: () => void;
  onSpeedChange: (speed: number) => void;
  className?: string;
}

const SPEEDS = [
  { value: 0.5, label: '0.5x' },
  { value: 1, label: '1x' },
  { value: 2, label: '2x' },
  { value: 4, label: '4x' },
];

export default function AutoPlayControls({
  isPlaying,
  speed,
  round,
  maxRounds,
  done,
  onTogglePlay,
  onSpeedChange,
  className,
}: AutoPlayControlsProps) {
  return (
    <motion.div
      className={cn('rounded-lg border border-primary/30 bg-primary/5 p-3', className)}
      initial={{ opacity: 0, height: 0 }}
      animate={{ opacity: 1, height: 'auto' }}
      exit={{ opacity: 0, height: 0 }}
    >
      <div className="mb-2 flex items-center justify-between">
        <span className="text-xs font-semibold text-primary">Auto-Play</span>
        <div className="flex items-center gap-1">
          {SPEEDS.map((s) => (
            <button
              key={s.value}
              onClick={() => onSpeedChange(s.value)}
              className={cn(
                'rounded px-1.5 py-0.5 text-[10px] font-bold transition-colors',
                speed === s.value
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground hover:bg-muted',
              )}
            >
              {s.label}
            </button>
          ))}
        </div>
      </div>
      <div className="flex items-center gap-2">
        <button
          onClick={onTogglePlay}
          disabled={done}
          className={cn(
            'flex items-center gap-1.5 rounded-md px-3 py-1.5 text-xs font-medium transition-colors',
            isPlaying
              ? 'bg-judge/20 text-judge hover:bg-judge/30'
              : 'bg-primary text-primary-foreground hover:bg-primary/90',
            done && 'opacity-50 cursor-not-allowed',
          )}
        >
          {isPlaying ? (
            <>
              <Pause className="h-3.5 w-3.5" /> Pause
            </>
          ) : done ? (
            <>
              <RotateCcw className="h-3.5 w-3.5" /> Done
            </>
          ) : (
            <>
              <Play className="h-3.5 w-3.5" /> Watch Episode
            </>
          )}
        </button>
        <div className="flex-1">
          <div className="h-1.5 w-full overflow-hidden rounded-full bg-muted">
            <motion.div
              className="h-full rounded-full bg-primary"
              animate={{ width: `${maxRounds > 0 ? (round / maxRounds) * 100 : 0}%` }}
              transition={{ duration: 0.3 }}
            />
          </div>
          <div className="mt-0.5 flex justify-between text-[10px] text-muted-foreground">
            <span>Round {round}</span>
            <span>{maxRounds} max</span>
          </div>
        </div>
      </div>
      {isPlaying && (
        <motion.div
          className="mt-2 flex items-center gap-1.5 text-[10px] text-primary"
          animate={{ opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 1.5, repeat: Infinity }}
        >
          <FastForward className="h-3 w-3" />
          Running at {speed}x speed...
        </motion.div>
      )}
    </motion.div>
  );
}

export function useAutoPlay(
  onStep: (() => void) | undefined,
  speed: number,
  isPlaying: boolean,
  done: boolean,
  loading: boolean,
) {
  const timerRef = useRef<ReturnType<typeof setTimeout>>();

  useEffect(() => {
    if (!isPlaying || done || loading || !onStep) {
      if (timerRef.current) clearTimeout(timerRef.current);
      return;
    }

    const delay = 3000 / speed;
    timerRef.current = setTimeout(() => {
      onStep();
    }, delay);

    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [isPlaying, done, loading, speed, onStep]);
}
