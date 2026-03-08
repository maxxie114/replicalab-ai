import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, ChevronRight, ChevronLeft, Sparkles } from 'lucide-react';
import AnimatedCharacter from '@/components/AnimatedCharacter';
import { cn } from '@/lib/utils';

const STEPS = [
  {
    title: 'Welcome to ReplicaLab',
    content: 'Watch AI agents negotiate how to replicate scientific experiments under real-world constraints.',
    character: null as string | null,
    highlight: null as string | null,
  },
  {
    title: 'Meet Dr. Elara — The Scientist',
    content: 'She proposes experiment protocols, adjusting sample size, technique, duration, and equipment to match the original paper.',
    character: 'scientist',
    highlight: 'scientist',
  },
  {
    title: 'Meet Takuma — The Lab Manager',
    content: 'He checks budgets, equipment availability, reagent stocks, and scheduling conflicts. If something doesn\'t work, he suggests alternatives.',
    character: 'lab_manager',
    highlight: 'lab_manager',
  },
  {
    title: 'Meet Judge Aldric',
    content: 'After negotiations end, the Judge scores the final protocol on Rigor, Feasibility, and Fidelity using a deterministic rubric.',
    character: 'judge',
    highlight: 'judge',
  },
  {
    title: 'How to Play',
    content: 'Choose a scenario and difficulty, then click "Start Episode". Use "Step" to advance rounds, or enable Auto-Play to watch it unfold. Try the Protocol Editor to craft your own actions!',
    character: null,
    highlight: null,
  },
  {
    title: 'Keyboard Shortcuts',
    content: 'Press Space to step, R to restart, A for auto-play, E to toggle the editor, and ? for the full shortcut list. You\'re ready!',
    character: null,
    highlight: null,
  },
];

const STORAGE_KEY = 'replicalab-onboarded';

export function useOnboarding() {
  const [show, setShow] = useState(false);

  useEffect(() => {
    try {
      if (!localStorage.getItem(STORAGE_KEY)) {
        setShow(true);
      }
    } catch {
      // ignore
    }
  }, []);

  function dismiss() {
    setShow(false);
    try {
      localStorage.setItem(STORAGE_KEY, '1');
    } catch {
      // ignore
    }
  }

  function reset() {
    setShow(true);
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch {
      // ignore
    }
  }

  return { showOnboarding: show, dismissOnboarding: dismiss, resetOnboarding: reset };
}

interface OnboardingProps {
  show: boolean;
  onDismiss: () => void;
}

export default function Onboarding({ show, onDismiss }: OnboardingProps) {
  const [step, setStep] = useState(0);

  if (!show) return null;

  const current = STEPS[step];
  const isLast = step === STEPS.length - 1;

  return (
    <AnimatePresence>
      <motion.div
        className="fixed inset-0 z-[200] flex items-center justify-center bg-background/70 backdrop-blur-sm"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
      >
        <motion.div
          className="relative w-full max-w-md rounded-2xl border border-border bg-card p-8 shadow-2xl"
          initial={{ scale: 0.9, y: 30 }}
          animate={{ scale: 1, y: 0 }}
          exit={{ scale: 0.9, y: 30 }}
          transition={{ type: 'spring', stiffness: 300, damping: 25 }}
        >
          {/* Skip button */}
          <button
            onClick={onDismiss}
            className="absolute top-3 right-3 rounded-md p-1 text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
          >
            <X className="h-4 w-4" />
          </button>

          {/* Step indicator */}
          <div className="mb-6 flex justify-center gap-1.5">
            {STEPS.map((_, i) => (
              <div
                key={i}
                className={cn(
                  'h-1.5 rounded-full transition-all duration-300',
                  i === step ? 'w-6 bg-primary' : 'w-1.5 bg-muted',
                )}
              />
            ))}
          </div>

          {/* Character */}
          <AnimatePresence mode="wait">
            <motion.div
              key={step}
              initial={{ opacity: 0, x: 30 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -30 }}
              className="flex flex-col items-center text-center"
            >
              {current.character ? (
                <div className="mb-4">
                  <AnimatedCharacter
                    role={current.character}
                    emotion="happy"
                    isActive
                    size="xl"
                    showAura
                    showEmoji={false}
                    showName
                  />
                </div>
              ) : (
                <div className="mb-4 flex h-20 w-20 items-center justify-center rounded-full bg-primary/10">
                  <Sparkles className="h-8 w-8 text-primary" />
                </div>
              )}

              <h2 className="mb-2 text-xl font-bold">{current.title}</h2>
              <p className="text-sm leading-relaxed text-muted-foreground">{current.content}</p>
            </motion.div>
          </AnimatePresence>

          {/* Navigation */}
          <div className="mt-8 flex items-center justify-between">
            <button
              onClick={() => setStep((s) => Math.max(0, s - 1))}
              disabled={step === 0}
              className="flex items-center gap-1 rounded-md px-3 py-1.5 text-sm text-muted-foreground hover:bg-muted disabled:opacity-30 transition-colors"
            >
              <ChevronLeft className="h-4 w-4" /> Back
            </button>

            {isLast ? (
              <button
                onClick={onDismiss}
                className="flex items-center gap-1 rounded-md bg-primary px-5 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors"
              >
                <Sparkles className="h-4 w-4" /> Let's Go!
              </button>
            ) : (
              <button
                onClick={() => setStep((s) => Math.min(STEPS.length - 1, s + 1))}
                className="flex items-center gap-1 rounded-md bg-primary px-4 py-1.5 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors"
              >
                Next <ChevronRight className="h-4 w-4" />
              </button>
            )}
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}
