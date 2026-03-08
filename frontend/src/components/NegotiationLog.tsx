import { useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { MessageSquare } from 'lucide-react';
import type { NegotiationMessage } from '@/types';
import { cn, roleBgColor, roleLabel } from '@/lib/utils';
import AnimatedCharacter from '@/components/AnimatedCharacter';

interface NegotiationLogProps {
  messages: NegotiationMessage[];
  className?: string;
}

export default function NegotiationLog({ messages, className }: NegotiationLogProps) {
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages.length]);

  return (
    <div className={cn('flex flex-col', className)}>
      <div className="flex items-center gap-2 border-b border-border px-4 py-3">
        <MessageSquare className="h-4 w-4 text-primary" />
        <h2 className="text-sm font-semibold">Negotiation Log</h2>
        <span className="ml-auto rounded-full bg-muted px-2 py-0.5 text-xs text-muted-foreground">
          {messages.length} messages
        </span>
      </div>

      <div className="flex-1 space-y-4 overflow-y-auto p-4">
        {messages.length === 0 ? (
          <div className="flex h-40 flex-col items-center justify-center gap-3 text-sm text-muted-foreground">
            <div className="flex items-center gap-6">
              <AnimatedCharacter role="scientist" emotion="idle" size="lg" showEmoji={false} showAura={false} />
              <span className="text-xl font-bold text-muted-foreground/30">VS</span>
              <AnimatedCharacter role="lab_manager" emotion="idle" size="lg" showEmoji={false} showAura={false} />
            </div>
            <p>Start an episode to see them negotiate</p>
          </div>
        ) : (
          messages.map((msg, i) => (
            <MessageBubble
              key={i}
              message={msg}
              index={i}
              isLatest={i === messages.length - 1}
            />
          ))
        )}
        <div ref={endRef} />
      </div>
    </div>
  );
}

function MessageBubble({
  message,
  index,
  isLatest,
}: {
  message: NegotiationMessage;
  index: number;
  isLatest: boolean;
}) {
  const isScientist = message.role === 'scientist';
  const actionType = message.action && 'action_type' in message.action
    ? message.action.action_type
    : undefined;

  return (
    <motion.div
      className={cn('flex gap-2.5', isScientist ? 'flex-row' : 'flex-row-reverse')}
      initial={{ opacity: 0, x: isScientist ? -20 : 20, y: 10 }}
      animate={{ opacity: 1, x: 0, y: 0 }}
      transition={{
        type: 'spring',
        stiffness: 300,
        damping: 25,
        delay: index * 0.1,
      }}
    >
      {/* Animated avatar */}
      <div className="mt-4 shrink-0">
        <AnimatedCharacter
          role={message.role}
          action={isLatest ? actionType : undefined}
          isSpeaking={isLatest}
          isActive={isLatest}
          size="md"
          showEmoji={isLatest}
          showAura={false}
          showName={false}
        />
      </div>

      <div className={cn('flex max-w-[78%] flex-col gap-1', isScientist ? 'items-start' : 'items-end')}>
        <div className="flex items-center gap-1.5 text-xs">
          <span className={cn('font-semibold', isScientist ? 'text-scientist' : 'text-lab-manager')}>
            {roleLabel(message.role)}
          </span>
          <span className="text-muted-foreground">· Round {message.round}</span>
        </div>

        <motion.div
          className={cn(
            'rounded-2xl border px-3.5 py-2.5 text-sm leading-relaxed',
            roleBgColor(message.role),
            isScientist ? 'rounded-tl-sm' : 'rounded-tr-sm',
          )}
          initial={{ scale: 0.9 }}
          animate={{ scale: 1 }}
          transition={{ type: 'spring', stiffness: 400, damping: 20, delay: index * 0.1 + 0.1 }}
        >
          {message.message}
        </motion.div>

        {actionType && (
          <motion.span
            className={cn(
              'inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[10px] font-medium',
              isScientist
                ? 'border-scientist/20 bg-scientist/5 text-scientist'
                : 'border-lab-manager/20 bg-lab-manager/5 text-lab-manager',
            )}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: index * 0.1 + 0.2 }}
          >
            {actionType.replace(/_/g, ' ')}
          </motion.span>
        )}
      </div>
    </motion.div>
  );
}
