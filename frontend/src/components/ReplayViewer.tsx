import { useState } from 'react';
import { History, ChevronLeft, ChevronRight, SkipBack, SkipForward } from 'lucide-react';
import type { NegotiationMessage } from '@/types';
import { cn, roleBgColor, roleLabel } from '@/lib/utils';
import CharacterAvatar from '@/components/CharacterAvatar';

interface ReplayViewerProps {
  messages: NegotiationMessage[];
  className?: string;
}

export default function ReplayViewer({ messages, className }: ReplayViewerProps) {
  const [currentIndex, setCurrentIndex] = useState(0);

  if (messages.length === 0) {
    return (
      <div className={cn('rounded-lg border border-border bg-card p-4', className)}>
        <div className="flex items-center gap-2">
          <History className="h-4 w-4 text-primary" />
          <h2 className="text-sm font-semibold">Replay</h2>
        </div>
        <p className="mt-4 text-center text-sm text-muted-foreground">No messages to replay</p>
      </div>
    );
  }

  const totalRounds = Math.max(...messages.map((m) => m.round));
  const currentRound = messages[currentIndex]?.round ?? 1;

  return (
    <div className={cn('rounded-lg border border-border bg-card p-4', className)}>
      <div className="mb-3 flex items-center gap-2">
        <History className="h-4 w-4 text-primary" />
        <h2 className="text-sm font-semibold">Replay</h2>
        <span className="ml-auto text-xs text-muted-foreground">Round {currentRound} / {totalRounds}</span>
      </div>
      <div className="mb-3">
        <input type="range" min={0} max={messages.length - 1} value={currentIndex}
          onChange={(e) => setCurrentIndex(parseInt(e.target.value, 10))} className="w-full accent-primary" />
        <div className="flex justify-between text-xs text-muted-foreground">
          <span>Message 1</span><span>Message {messages.length}</span>
        </div>
      </div>
      <div className="mb-3 flex items-center justify-center gap-2">
        <ScrubBtn icon={<SkipBack className="h-3.5 w-3.5" />} onClick={() => setCurrentIndex(0)} disabled={currentIndex === 0} />
        <ScrubBtn icon={<ChevronLeft className="h-3.5 w-3.5" />} onClick={() => setCurrentIndex(Math.max(0, currentIndex - 1))} disabled={currentIndex === 0} />
        <span className="w-20 text-center text-xs font-medium">{currentIndex + 1} / {messages.length}</span>
        <ScrubBtn icon={<ChevronRight className="h-3.5 w-3.5" />} onClick={() => setCurrentIndex(Math.min(messages.length - 1, currentIndex + 1))} disabled={currentIndex === messages.length - 1} />
        <ScrubBtn icon={<SkipForward className="h-3.5 w-3.5" />} onClick={() => setCurrentIndex(messages.length - 1)} disabled={currentIndex === messages.length - 1} />
      </div>
      {messages[currentIndex] && (
        <div className="flex items-start gap-2.5">
          <CharacterAvatar role={messages[currentIndex].role} size="sm" className="mt-1 shrink-0" />
          <div className={cn('flex-1 rounded-lg border px-3 py-2 text-sm', roleBgColor(messages[currentIndex].role))}>
            <div className="mb-1 text-xs font-medium">{roleLabel(messages[currentIndex].role)} · Round {messages[currentIndex].round}</div>
            {messages[currentIndex].message}
          </div>
        </div>
      )}
    </div>
  );
}

function ScrubBtn({ icon, onClick, disabled }: { icon: React.ReactNode; onClick: () => void; disabled: boolean }) {
  return (
    <button onClick={onClick} disabled={disabled}
      className="rounded-md border border-border p-1.5 text-muted-foreground transition-colors hover:bg-muted disabled:opacity-30">
      {icon}
    </button>
  );
}
