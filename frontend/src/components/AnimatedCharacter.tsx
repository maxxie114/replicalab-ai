import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '@/lib/utils';

export type CharacterEmotion =
  | 'idle'
  | 'thinking'
  | 'speaking'
  | 'happy'
  | 'concerned'
  | 'analyzing'
  | 'approving'
  | 'rejecting'
  | 'judging'
  | 'celebrating';

export type ActionAnimation =
  | 'propose_protocol'
  | 'revise_protocol'
  | 'request_info'
  | 'accept'
  | 'report_feasibility'
  | 'suggest_substitution'
  | 'reject'
  | 'scoring'
  | 'verdict_success'
  | 'verdict_failure'
  | 'verdict_partial';

const CHARACTER_IMAGES: Record<string, string> = {
  scientist: '/characters/scientist.png',
  lab_manager: '/characters/lab-manager.png',
  judge: '/characters/judge.png',
};

const EMOTION_EMOJIS: Record<CharacterEmotion, string> = {
  idle: '',
  thinking: '🤔',
  speaking: '💬',
  happy: '😊',
  concerned: '😟',
  analyzing: '🔍',
  approving: '✅',
  rejecting: '❌',
  judging: '⚖️',
  celebrating: '🎉',
};

const ACTION_TO_EMOTION: Record<string, CharacterEmotion> = {
  propose_protocol: 'speaking',
  revise_protocol: 'thinking',
  request_info: 'thinking',
  accept: 'happy',
  report_feasibility: 'analyzing',
  suggest_substitution: 'thinking',
  reject: 'concerned',
  scoring: 'judging',
  verdict_success: 'celebrating',
  verdict_failure: 'rejecting',
  verdict_partial: 'concerned',
};

const idleFloat = {
  y: [0, -6, 0],
  transition: {
    duration: 3,
    repeat: Infinity,
    ease: 'easeInOut' as const,
  },
};

const speakingBounce = {
  scale: [1, 1.05, 1],
  transition: {
    duration: 0.4,
    repeat: 3,
    ease: 'easeInOut' as const,
  },
};

const thinkingTilt = {
  rotate: [0, -5, 5, -3, 0],
  transition: {
    duration: 1.2,
    repeat: 2,
    ease: 'easeInOut' as const,
  },
};

const happyJump = {
  y: [0, -20, 0, -12, 0],
  scale: [1, 1.1, 1, 1.05, 1],
  transition: {
    duration: 0.8,
    ease: 'easeOut' as const,
  },
};

const rejectShake = {
  x: [0, -8, 8, -6, 6, -3, 0],
  transition: {
    duration: 0.6,
    ease: 'easeInOut' as const,
  },
};

const analyzingPulse = {
  scale: [1, 1.03, 1],
  opacity: [1, 0.85, 1],
  transition: {
    duration: 1.5,
    repeat: 2,
    ease: 'easeInOut' as const,
  },
};

const celebrateAnimation = {
  y: [0, -25, 0, -15, 0, -8, 0],
  rotate: [0, -10, 10, -5, 5, 0],
  scale: [1, 1.15, 1, 1.1, 1, 1.05, 1],
  transition: {
    duration: 1.2,
    ease: 'easeOut' as const,
  },
};

function getAnimationForEmotion(emotion: CharacterEmotion) {
  switch (emotion) {
    case 'speaking':
      return speakingBounce;
    case 'thinking':
      return thinkingTilt;
    case 'happy':
    case 'approving':
      return happyJump;
    case 'concerned':
    case 'rejecting':
      return rejectShake;
    case 'analyzing':
    case 'judging':
      return analyzingPulse;
    case 'celebrating':
      return celebrateAnimation;
    default:
      return idleFloat;
  }
}

const AURA_COLORS: Record<string, string> = {
  scientist: 'from-scientist/40 to-scientist/0',
  lab_manager: 'from-lab-manager/40 to-lab-manager/0',
  judge: 'from-judge/40 to-judge/0',
};

const RING_ACTIVE: Record<string, string> = {
  scientist: 'ring-scientist shadow-[0_0_20px_rgba(59,130,246,0.5)]',
  lab_manager: 'ring-lab-manager shadow-[0_0_20px_rgba(16,185,129,0.5)]',
  judge: 'ring-judge shadow-[0_0_20px_rgba(245,158,11,0.5)]',
};

interface AnimatedCharacterProps {
  role: string;
  emotion?: CharacterEmotion;
  action?: string;
  isSpeaking?: boolean;
  isActive?: boolean;
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'stage';
  showEmoji?: boolean;
  showAura?: boolean;
  showName?: boolean;
  className?: string;
}

const sizeMap = {
  sm: 'h-10 w-10',
  md: 'h-16 w-16',
  lg: 'h-24 w-24',
  xl: 'h-36 w-36',
  stage: 'h-44 w-44',
};

export default function AnimatedCharacter({
  role,
  emotion: emotionProp,
  action,
  isSpeaking = false,
  isActive = false,
  size = 'lg',
  showEmoji = true,
  showAura = true,
  showName = true,
  className,
}: AnimatedCharacterProps) {
  const [currentEmotion, setCurrentEmotion] = useState<CharacterEmotion>('idle');
  const [particles, setParticles] = useState<number[]>([]);

  useEffect(() => {
    if (emotionProp) {
      setCurrentEmotion(emotionProp);
      return;
    }
    if (action && ACTION_TO_EMOTION[action]) {
      setCurrentEmotion(ACTION_TO_EMOTION[action]);
    } else if (isSpeaking) {
      setCurrentEmotion('speaking');
    } else {
      setCurrentEmotion('idle');
    }
  }, [emotionProp, action, isSpeaking]);

  useEffect(() => {
    if (currentEmotion === 'celebrating' || currentEmotion === 'happy') {
      setParticles(Array.from({ length: 6 }, (_, i) => i));
      const timer = setTimeout(() => setParticles([]), 2000);
      return () => clearTimeout(timer);
    }
  }, [currentEmotion]);

  const anim = getAnimationForEmotion(currentEmotion);
  const emoji = EMOTION_EMOJIS[currentEmotion];
  const src = CHARACTER_IMAGES[role];
  const names: Record<string, string> = { scientist: 'Dr. Elara', lab_manager: 'Takuma', judge: 'Judge Aldric' };

  return (
    <div className={cn('relative flex flex-col items-center', className)}>
      {/* Aura glow */}
      {showAura && isActive && (
        <motion.div
          className={cn(
            'absolute inset-0 rounded-full bg-gradient-radial',
            AURA_COLORS[role],
          )}
          animate={{
            scale: [1, 1.3, 1],
            opacity: [0.3, 0.6, 0.3],
          }}
          transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
          style={{ filter: 'blur(20px)' }}
        />
      )}

      {/* Particles */}
      <AnimatePresence>
        {particles.map((p) => (
          <motion.div
            key={`particle-${p}`}
            className="absolute text-lg pointer-events-none"
            initial={{
              opacity: 1,
              x: 0,
              y: 0,
              scale: 0.5,
            }}
            animate={{
              opacity: 0,
              x: (Math.random() - 0.5) * 100,
              y: -60 - Math.random() * 40,
              scale: 1,
            }}
            exit={{ opacity: 0 }}
            transition={{ duration: 1 + Math.random() * 0.5, ease: 'easeOut' }}
          >
            {['✨', '⭐', '🌟', '💫', '🔬', '🧪'][p % 6]}
          </motion.div>
        ))}
      </AnimatePresence>

      {/* Emoji indicator */}
      {showEmoji && emoji && (
        <motion.div
          key={currentEmotion}
          className="absolute -top-2 -right-2 z-10 text-xl"
          initial={{ scale: 0, rotate: -45 }}
          animate={{ scale: 1, rotate: 0 }}
          transition={{ type: 'spring', stiffness: 400, damping: 15 }}
        >
          {emoji}
        </motion.div>
      )}

      {/* Character image */}
      <motion.div
        className={cn(
          'relative overflow-hidden rounded-full ring-3 bg-muted transition-shadow duration-300',
          sizeMap[size],
          isActive ? RING_ACTIVE[role] : `ring-${role === 'scientist' ? 'scientist' : role === 'lab_manager' ? 'lab-manager' : 'judge'}/30`,
        )}
        animate={anim}
      >
        {src && (
          <img
            src={src}
            alt={names[role] ?? role}
            className="h-full w-full object-cover object-top"
            draggable={false}
          />
        )}

        {/* Speaking indicator overlay */}
        {isSpeaking && (
          <motion.div
            className="absolute inset-0 rounded-full border-2 border-white/40"
            animate={{ scale: [1, 1.15, 1], opacity: [0.5, 0, 0.5] }}
            transition={{ duration: 1.2, repeat: Infinity }}
          />
        )}
      </motion.div>

      {/* Typing dots */}
      {currentEmotion === 'thinking' && (
        <div className="mt-1 flex items-center gap-1">
          {[0, 1, 2].map((i) => (
            <motion.div
              key={i}
              className={cn(
                'h-1.5 w-1.5 rounded-full',
                role === 'scientist' ? 'bg-scientist' : role === 'lab_manager' ? 'bg-lab-manager' : 'bg-judge',
              )}
              animate={{ y: [0, -4, 0] }}
              transition={{ duration: 0.6, repeat: Infinity, delay: i * 0.15 }}
            />
          ))}
        </div>
      )}

      {/* Name */}
      {showName && (
        <motion.span
          className={cn(
            'mt-1.5 text-xs font-semibold',
            role === 'scientist' ? 'text-scientist' : role === 'lab_manager' ? 'text-lab-manager' : 'text-judge',
          )}
          animate={isActive ? { opacity: [0.7, 1, 0.7] } : { opacity: 1 }}
          transition={isActive ? { duration: 2, repeat: Infinity } : {}}
        >
          {names[role]}
        </motion.span>
      )}
    </div>
  );
}
