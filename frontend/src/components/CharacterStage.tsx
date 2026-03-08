import { Suspense } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import type { NegotiationMessage, ScoreBreakdown, JudgeAudit } from '@/types';
import AnimatedCharacter from '@/components/AnimatedCharacter';
import MoleculeScene from '@/components/MoleculeScene';
import { cn, formatScore } from '@/lib/utils';

type EpisodePhase = 'waiting' | 'negotiating' | 'judging' | 'complete';

interface CharacterStageProps {
  phase: EpisodePhase;
  round: number;
  maxRounds: number;
  lastMessage?: NegotiationMessage;
  scores?: ScoreBreakdown | null;
  judgeAudit?: JudgeAudit | null;
  className?: string;
}

function getActionFromMessage(msg?: NegotiationMessage): string | undefined {
  if (!msg?.action) return undefined;
  if ('action_type' in msg.action) return msg.action.action_type;
  return undefined;
}

export default function CharacterStage({
  phase,
  round,
  maxRounds,
  lastMessage,
  scores,
  judgeAudit,
  className,
}: CharacterStageProps) {
  const lastAction = getActionFromMessage(lastMessage);
  const speakingRole = lastMessage?.role;

  const scientistAction =
    speakingRole === 'scientist' ? lastAction : undefined;
  const labManagerAction =
    speakingRole === 'lab_manager' ? lastAction : undefined;

  const judgeAction =
    phase === 'judging'
      ? 'scoring'
      : phase === 'complete' && judgeAudit
        ? `verdict_${judgeAudit.verdict}`
        : undefined;

  return (
    <div className={cn('relative rounded-xl border border-border bg-card overflow-hidden', className)}>
      {/* 3D particle background */}
      <Suspense fallback={null}>
        <MoleculeScene className="absolute inset-0 z-0 opacity-15" variant="stage" />
      </Suspense>
      <div className="absolute inset-0 bg-gradient-to-b from-primary/5 via-transparent to-transparent" />

      {/* Round indicator */}
      <div className="relative flex items-center justify-center gap-1.5 border-b border-border bg-muted/30 px-4 py-2">
        <PhaseIndicator phase={phase} />
        <span className="text-xs font-medium text-muted-foreground">
          Round {round}/{maxRounds}
        </span>
        {phase === 'negotiating' && (
          <div className="ml-2 flex gap-0.5">
            {Array.from({ length: maxRounds }, (_, i) => (
              <div
                key={i}
                className={cn(
                  'h-1.5 w-4 rounded-full transition-colors',
                  i < round ? 'bg-primary' : 'bg-muted',
                )}
              />
            ))}
          </div>
        )}
      </div>

      {/* Stage area */}
      <div className="relative flex items-center justify-center gap-4 px-6 py-6 md:gap-8 md:px-10">
        {/* Scientist */}
        <motion.div
          className="flex flex-col items-center"
          initial={{ x: -40, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ type: 'spring', stiffness: 200, damping: 20 }}
        >
          <AnimatedCharacter
            role="scientist"
            action={scientistAction}
            isSpeaking={speakingRole === 'scientist'}
            isActive={phase === 'negotiating' && speakingRole === 'scientist'}
            size="stage"
            showAura
            showEmoji
          />
        </motion.div>

        {/* Center: VS / action indicator */}
        <div className="flex flex-col items-center gap-2">
          <AnimatePresence mode="wait">
            {phase === 'waiting' && (
              <motion.div
                key="vs"
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                exit={{ scale: 0, opacity: 0 }}
                className="text-2xl font-black text-muted-foreground/30"
              >
                VS
              </motion.div>
            )}

            {phase === 'negotiating' && lastMessage && (
              <motion.div
                key={`action-${lastMessage.timestamp}`}
                initial={{ scale: 0, y: 10 }}
                animate={{ scale: 1, y: 0 }}
                exit={{ scale: 0, opacity: 0 }}
                transition={{ type: 'spring', stiffness: 300, damping: 20 }}
                className="flex flex-col items-center gap-1"
              >
                <ActionBadge action={lastAction} role={lastMessage.role} />
                <motion.div
                  className="h-8 w-px bg-border"
                  initial={{ scaleY: 0 }}
                  animate={{ scaleY: 1 }}
                  transition={{ delay: 0.2 }}
                />
                <SpeechPreview message={lastMessage.message} role={lastMessage.role} />
              </motion.div>
            )}

            {phase === 'judging' && (
              <motion.div
                key="judging"
                initial={{ scale: 0 }}
                animate={{ scale: 1, rotate: [0, -5, 5, 0] }}
                transition={{ type: 'spring', stiffness: 200 }}
                className="flex flex-col items-center"
              >
                <AnimatedCharacter
                  role="judge"
                  action="scoring"
                  isActive
                  size="lg"
                  showAura
                  showEmoji
                  showName
                />
              </motion.div>
            )}

            {phase === 'complete' && scores && (
              <motion.div
                key="scores"
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: 'spring', stiffness: 200, delay: 0.3 }}
                className="flex flex-col items-center gap-2"
              >
                <AnimatedCharacter
                  role="judge"
                  action={judgeAction}
                  isActive
                  size="lg"
                  showAura
                  showEmoji
                  showName
                />
                <motion.div
                  className="mt-1 rounded-lg bg-judge/10 border border-judge/30 px-3 py-2 text-center"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.5 }}
                >
                  <div className="text-2xl font-black text-judge">
                    {scores.total_reward.toFixed(1)}
                  </div>
                  <div className="flex gap-3 text-[10px] text-muted-foreground mt-0.5">
                    <span>R:{formatScore(scores.rigor)}</span>
                    <span>F:{formatScore(scores.feasibility)}</span>
                    <span>D:{formatScore(scores.fidelity)}</span>
                  </div>
                </motion.div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Lab Manager */}
        <motion.div
          className="flex flex-col items-center"
          initial={{ x: 40, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ type: 'spring', stiffness: 200, damping: 20 }}
        >
          <AnimatedCharacter
            role="lab_manager"
            action={labManagerAction}
            isSpeaking={speakingRole === 'lab_manager'}
            isActive={phase === 'negotiating' && speakingRole === 'lab_manager'}
            size="stage"
            showAura
            showEmoji
          />
        </motion.div>
      </div>

      {/* Judge observer during negotiation */}
      {phase === 'negotiating' && (
        <motion.div
          className="absolute top-2 right-4 z-10 flex flex-col items-center"
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.5, type: 'spring' }}
        >
          <AnimatedCharacter
            role="judge"
            emotion="thinking"
            isActive={false}
            size="sm"
            showAura={false}
            showEmoji={false}
            showName={false}
          />
          <span className="mt-0.5 text-[9px] font-medium text-judge/60">Observing</span>
        </motion.div>
      )}

      {/* Energy bar / tension indicator */}
      {phase === 'negotiating' && (
        <motion.div
          className="mx-6 mb-4 h-1 overflow-hidden rounded-full bg-muted"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <motion.div
            className="h-full rounded-full bg-gradient-to-r from-scientist via-primary to-lab-manager"
            animate={{ width: `${(round / maxRounds) * 100}%` }}
            transition={{ duration: 0.5 }}
          />
        </motion.div>
      )}
    </div>
  );
}

function PhaseIndicator({ phase }: { phase: EpisodePhase }) {
  const config = {
    waiting: { label: 'Ready', color: 'bg-muted-foreground' },
    negotiating: { label: 'Negotiating', color: 'bg-primary' },
    judging: { label: 'Judging', color: 'bg-judge' },
    complete: { label: 'Complete', color: 'bg-lab-manager' },
  }[phase];

  return (
    <div className="flex items-center gap-1.5">
      <motion.div
        className={cn('h-2 w-2 rounded-full', config.color)}
        animate={
          phase === 'negotiating' || phase === 'judging'
            ? { scale: [1, 1.4, 1], opacity: [1, 0.6, 1] }
            : {}
        }
        transition={{ duration: 1.2, repeat: Infinity }}
      />
      <span className="text-xs font-semibold">{config.label}</span>
    </div>
  );
}

function ActionBadge({ action, role }: { action?: string; role: string }) {
  if (!action) return null;
  const label = action.replace(/_/g, ' ');
  const color = role === 'scientist' ? 'bg-scientist/20 text-scientist border-scientist/30'
    : 'bg-lab-manager/20 text-lab-manager border-lab-manager/30';

  return (
    <motion.span
      className={cn('rounded-full border px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wider', color)}
      initial={{ scale: 0 }}
      animate={{ scale: 1 }}
      transition={{ type: 'spring', stiffness: 400 }}
    >
      {label}
    </motion.span>
  );
}

function SpeechPreview({ message, role }: { message: string; role: string }) {
  const truncated = message.length > 80 ? message.slice(0, 80) + '...' : message;
  const bgColor = role === 'scientist' ? 'bg-scientist/5 border-scientist/20'
    : 'bg-lab-manager/5 border-lab-manager/20';

  return (
    <motion.div
      className={cn('max-w-[200px] rounded-lg border px-2.5 py-1.5 text-[11px] leading-snug text-muted-foreground', bgColor)}
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay: 0.3 }}
    >
      {truncated}
    </motion.div>
  );
}
