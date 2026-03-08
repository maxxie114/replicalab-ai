import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Keyboard, X } from 'lucide-react';
import { cn } from '@/lib/utils';

interface KeyboardShortcutsProps {
  onStep?: () => void;
  onRestart?: () => void;
  onAutoPlay?: () => void;
  onToggleEditor?: () => void;
  disabled?: boolean;
}

const SHORTCUTS = [
  { key: 'Space', label: 'Step / Start', action: 'step' },
  { key: 'R', label: 'Restart episode', action: 'restart' },
  { key: 'A', label: 'Toggle auto-play', action: 'autoplay' },
  { key: 'E', label: 'Toggle protocol editor', action: 'editor' },
  { key: '1', label: 'Easy difficulty', action: 'diff1' },
  { key: '2', label: 'Medium difficulty', action: 'diff2' },
  { key: '3', label: 'Hard difficulty', action: 'diff3' },
  { key: '?', label: 'Show shortcuts', action: 'help' },
  { key: 'Esc', label: 'Close overlays', action: 'close' },
];

export function useKeyboardShortcuts({
  onStep,
  onRestart,
  onAutoPlay,
  onToggleEditor,
  disabled,
}: KeyboardShortcutsProps) {
  const [showHelp, setShowHelp] = useState(false);

  useEffect(() => {
    function handler(e: KeyboardEvent) {
      // Don't trigger when typing in inputs
      const tag = (e.target as HTMLElement)?.tagName;
      if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return;

      if (disabled && e.key !== '?' && e.key !== 'Escape') return;

      switch (e.key) {
        case ' ':
          e.preventDefault();
          onStep?.();
          break;
        case 'r':
        case 'R':
          onRestart?.();
          break;
        case 'a':
        case 'A':
          onAutoPlay?.();
          break;
        case 'e':
        case 'E':
          onToggleEditor?.();
          break;
        case '?':
          setShowHelp((p) => !p);
          break;
        case 'Escape':
          setShowHelp(false);
          break;
      }
    }
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [onStep, onRestart, onAutoPlay, onToggleEditor, disabled]);

  return { showHelp, setShowHelp };
}

export function ShortcutsOverlay({ show, onClose }: { show: boolean; onClose: () => void }) {
  return (
    <AnimatePresence>
      {show && (
        <motion.div
          className="fixed inset-0 z-[90] flex items-center justify-center bg-background/60 backdrop-blur-sm"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
        >
          <motion.div
            className="w-full max-w-sm rounded-xl border border-border bg-card p-6 shadow-2xl"
            initial={{ scale: 0.9, y: 20 }}
            animate={{ scale: 1, y: 0 }}
            exit={{ scale: 0.9, y: 20 }}
            onClick={(e) => e.stopPropagation()}
          >
            <div className="mb-4 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Keyboard className="h-5 w-5 text-primary" />
                <h2 className="text-lg font-bold">Keyboard Shortcuts</h2>
              </div>
              <button onClick={onClose} className="rounded-md p-1 text-muted-foreground hover:bg-muted">
                <X className="h-4 w-4" />
              </button>
            </div>
            <div className="space-y-1.5">
              {SHORTCUTS.map((s) => (
                <div key={s.key} className="flex items-center justify-between rounded-md px-2 py-1.5 text-sm hover:bg-muted/50">
                  <span className="text-muted-foreground">{s.label}</span>
                  <kbd className="rounded-md border border-border bg-muted px-2 py-0.5 font-mono text-xs font-semibold">
                    {s.key}
                  </kbd>
                </div>
              ))}
            </div>
            <p className="mt-4 text-center text-xs text-muted-foreground">
              Press <kbd className="rounded border border-border bg-muted px-1 font-mono text-[10px]">?</kbd> anytime to toggle
            </p>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

export function ShortcutHint({ className }: { className?: string }) {
  return (
    <span className={cn('inline-flex items-center gap-1 text-[10px] text-muted-foreground/60', className)}>
      Press <kbd className="rounded border border-border/50 bg-muted/50 px-1 font-mono">?</kbd> for shortcuts
    </span>
  );
}
