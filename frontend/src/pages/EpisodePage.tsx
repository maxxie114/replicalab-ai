import { useState, useCallback, useMemo, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import type { EpisodeState, ResetParams } from '@/types';
import { createMockEpisodeState } from '@/lib/api';
import { sfx } from '@/lib/audio';
import PaperPanel from '@/components/PaperPanel';
import NegotiationLog from '@/components/NegotiationLog';
import ProtocolPanel from '@/components/ProtocolPanel';
import ScorePanel from '@/components/ScorePanel';
import Controls from '@/components/Controls';
import LabInventory from '@/components/LabInventory';
import JudgeAuditPanel from '@/components/JudgeAuditPanel';
import ReplayViewer from '@/components/ReplayViewer';
import CharacterStage from '@/components/CharacterStage';
import AnimatedCharacter from '@/components/AnimatedCharacter';

export default function EpisodePage() {
  const [episode, setEpisode] = useState<EpisodeState | null>(null);
  const [loading, setLoading] = useState(false);
  const [isJudging, setIsJudging] = useState(false);

  const phase = useMemo(() => {
    if (!episode) return 'waiting' as const;
    if (isJudging) return 'judging' as const;
    if (episode.done) return 'complete' as const;
    return 'negotiating' as const;
  }, [episode, isJudging]);

  const lastMessage = useMemo(() => {
    if (!episode?.conversation.length) return undefined;
    return episode.conversation[episode.conversation.length - 1];
  }, [episode]);

  const prevPhaseRef = useRef(phase);
  const prevMsgCountRef = useRef(0);

  useEffect(() => {
    const prev = prevPhaseRef.current;
    prevPhaseRef.current = phase;

    if (prev === 'waiting' && phase === 'negotiating') {
      sfx.episodeStart();
    } else if (phase === 'judging' && prev !== 'judging') {
      sfx.judgeAppear();
      setTimeout(() => sfx.gavel(), 1500);
    } else if (phase === 'complete' && prev !== 'complete') {
      sfx.scoreReveal();
      if (episode?.judge_audit?.verdict === 'success') {
        setTimeout(() => sfx.success(), 400);
      } else if (episode?.judge_audit?.verdict) {
        setTimeout(() => sfx.failure(), 400);
      }
    }
  }, [phase, episode?.judge_audit?.verdict]);

  useEffect(() => {
    if (!episode?.conversation.length) return;
    const count = episode.conversation.length;
    if (count > prevMsgCountRef.current) {
      const latest = episode.conversation[count - 1];
      if (latest.role === 'scientist') sfx.scientistSpeak();
      else sfx.labManagerSpeak();

      if (count > 1) sfx.roundTick();
    }
    prevMsgCountRef.current = count;
  }, [episode?.conversation]);

  const handleStart = useCallback(async (_params: ResetParams) => {
    setLoading(true);
    setIsJudging(false);
    sfx.click();
    try {
      const state = createMockEpisodeState(false);
      setEpisode(state);
    } catch (err) {
      console.error('Failed to start episode:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleStep = useCallback(async () => {
    if (!episode || episode.done) return;
    setLoading(true);
    sfx.negotiate();

    setIsJudging(true);
    await new Promise((r) => setTimeout(r, 4000));
    setIsJudging(false);

    try {
      const state = createMockEpisodeState(true);
      setEpisode(state);
    } catch (err) {
      console.error('Failed to step episode:', err);
    } finally {
      setLoading(false);
    }
  }, [episode]);

  if (!episode) {
    return (
      <div className="mx-auto max-w-screen-2xl p-4">
        <div className="flex flex-col items-center justify-center py-16">
          {/* Pre-game character intro - all 3 characters */}
          <motion.div
            className="mb-8 flex items-end justify-center gap-8"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <div className="flex flex-col items-center">
              <AnimatedCharacter
                role="scientist"
                emotion="idle"
                isActive={false}
                size="xl"
                showAura={false}
                showEmoji={false}
              />
              <span className="mt-1 text-xs font-semibold text-scientist">Dr. Elara</span>
            </div>
            <motion.div
              className="mb-12 flex flex-col items-center"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.3, type: 'spring' }}
            >
              <span className="text-2xl font-black text-muted-foreground/20">VS</span>
            </motion.div>
            <div className="flex flex-col items-center">
              <AnimatedCharacter
                role="lab_manager"
                emotion="idle"
                isActive={false}
                size="xl"
                showAura={false}
                showEmoji={false}
              />
              <span className="mt-1 text-xs font-semibold text-lab-manager">Takuma</span>
            </div>
            <motion.div
              className="mb-12 flex flex-col items-center"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
            >
              <span className="text-xs font-bold text-muted-foreground/30">then</span>
            </motion.div>
            <motion.div
              className="flex flex-col items-center"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.6, type: 'spring' }}
            >
              <AnimatedCharacter
                role="judge"
                emotion="idle"
                isActive={false}
                size="xl"
                showAura={false}
                showEmoji={false}
              />
              <span className="mt-1 text-xs font-semibold text-judge">Aldric</span>
            </motion.div>
          </motion.div>

          <motion.div
            className="mb-8 text-center"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
          >
            <h1 className="mb-2 text-2xl font-bold">Start a New Episode</h1>
            <p className="text-muted-foreground">Choose a scenario, set difficulty, and watch them negotiate</p>
          </motion.div>

          <motion.div
            className="w-full max-w-sm"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
          >
            <Controls onStart={handleStart} disabled={loading} episodeActive={false} />
          </motion.div>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-screen-2xl p-4">
      {/* Character Stage - full width above the panels */}
      <AnimatePresence>
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-4"
        >
          <CharacterStage
            phase={phase}
            round={episode.round}
            maxRounds={episode.max_rounds}
            lastMessage={lastMessage}
            scores={episode.scores}
            judgeAudit={episode.judge_audit}
          />
        </motion.div>
      </AnimatePresence>

      {/* Three-panel layout */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-12">
        {/* Left panel */}
        <motion.div
          className="space-y-4 lg:col-span-3"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
        >
          <PaperPanel
            paper={episode.paper}
            seed={episode.seed}
            template={episode.template}
            difficulty={episode.difficulty}
            round={episode.round}
            maxRounds={episode.max_rounds}
            episodeId={episode.episode_id}
          />
          <LabInventory constraints={episode.lab_constraints} />
          <Controls
            onStart={handleStart}
            onStep={!episode.done ? handleStep : undefined}
            disabled={loading}
            episodeActive={true}
          />
        </motion.div>

        {/* Center panel */}
        <motion.div
          className="flex flex-col lg:col-span-5"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <NegotiationLog
            messages={episode.conversation}
            className="min-h-[400px] rounded-lg border border-border bg-card"
          />
          {episode.done && episode.judge_audit && (
            <motion.div
              className="mt-4"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.5 }}
            >
              <JudgeAuditPanel audit={episode.judge_audit} />
            </motion.div>
          )}
        </motion.div>

        {/* Right panel */}
        <motion.div
          className="space-y-4 lg:col-span-4"
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
        >
          <ProtocolPanel protocol={episode.protocol} paper={episode.paper} />
          <ScorePanel scores={episode.scores} done={episode.done} />
          {episode.done && <ReplayViewer messages={episode.conversation} />}
        </motion.div>
      </div>
    </div>
  );
}
