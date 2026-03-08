import { useState, useCallback, useMemo, useEffect, useRef, Suspense } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import type { EpisodeState, ResetParams, ScientistAction } from '@/types';
import { resetEpisode, stepEpisode, buildDefaultScientistAction, buildAcceptAction } from '@/lib/api';
import { sfx, startAmbient, stopAmbient } from '@/lib/audio';
import { fireSuccessConfetti, fireGavelConfetti } from '@/lib/confetti';
import { useToast } from '@/components/Toast';
import { useKeyboardShortcuts, ShortcutsOverlay, ShortcutHint } from '@/components/KeyboardShortcuts';
import AutoPlayControls, { useAutoPlay } from '@/components/AutoPlayControls';
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
import LiveScoreGauges from '@/components/LiveScoreGauges';
import ProtocolTimeline from '@/components/ProtocolTimeline';
import AgentThoughts from '@/components/AgentThoughts';
import ProtocolEditor from '@/components/ProtocolEditor';
import LabScene3D from '@/components/LabScene3D';

export default function EpisodePage() {
  const { episodeId: routeEpisodeId } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();

  const [episode, setEpisode] = useState<EpisodeState | null>(null);
  const [loading, setLoading] = useState(false);
  const [isJudging, setIsJudging] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Feature 5: Auto-play
  const [autoPlaying, setAutoPlaying] = useState(false);
  const [autoSpeed, setAutoSpeed] = useState(1);

  // Feature 11: Protocol editor toggle
  const [showEditor, setShowEditor] = useState(false);

  // Feature 13: 3D lab toggle
  const [show3DLab, setShow3DLab] = useState(false);

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

  // Sound effects for phase transitions
  const prevPhaseRef = useRef(phase);
  const prevMsgCountRef = useRef(0);

  useEffect(() => {
    const prev = prevPhaseRef.current;
    prevPhaseRef.current = phase;

    if (prev === 'waiting' && phase === 'negotiating') {
      sfx.episodeStart();
      startAmbient();
    } else if (phase === 'judging' && prev !== 'judging') {
      sfx.judgeAppear();
      setTimeout(() => {
        sfx.gavel();
        fireGavelConfetti();
      }, 1500);
    } else if (phase === 'complete' && prev !== 'complete') {
      stopAmbient();
      sfx.scoreReveal();
      const verdict = episode?.judge_audit?.verdict;
      if (verdict === 'accept' || verdict === 'success') {
        setTimeout(() => {
          sfx.success();
          fireSuccessConfetti();
        }, 400);
        toast('Episode complete — Agreement reached!', 'success');
      } else if (verdict) {
        setTimeout(() => sfx.failure(), 400);
        toast(`Episode complete — Verdict: ${verdict}`, 'warning');
      }
    }
  }, [phase, episode?.judge_audit?.verdict, toast]);

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

  // Cleanup ambient on unmount
  useEffect(() => {
    return () => stopAmbient();
  }, []);

  const handleStart = useCallback(async (params: ResetParams) => {
    setLoading(true);
    setIsJudging(false);
    setError(null);
    setAutoPlaying(false);
    sfx.click();
    try {
      const state = await resetEpisode(params);
      setEpisode(state);
      prevMsgCountRef.current = 0;
      toast('Episode started!', 'info');
      // Feature 9: Update URL for shareable link
      navigate(`/episode/${state.episode_id}`, { replace: true });
    } catch (err) {
      console.error('Failed to start episode:', err);
      const msg = err instanceof Error ? err.message : 'Failed to start episode';
      setError(msg);
      toast(msg, 'error');
    } finally {
      setLoading(false);
    }
  }, [toast, navigate]);

  const handleStepWithAction = useCallback(async (action?: ScientistAction) => {
    if (!episode || episode.done) return;
    setLoading(true);
    setError(null);

    if (!action) {
      sfx.negotiate();
    }

    try {
      const isLastRound = episode.round >= episode.max_rounds - 1;
      const finalAction = action ?? (isLastRound ? buildAcceptAction() : buildDefaultScientistAction());

      if (isLastRound && !action) {
        setIsJudging(true);
        await new Promise((r) => setTimeout(r, 2000));
      }

      const state = await stepEpisode(episode.session_id, finalAction, episode);

      if (state.done && !isLastRound) {
        setIsJudging(true);
        await new Promise((r) => setTimeout(r, 2000));
      }

      setIsJudging(false);
      setEpisode(state);
      sfx.protocolChange();
      toast(`Round ${state.round}/${state.max_rounds}`, 'info');
    } catch (err) {
      console.error('Failed to step episode:', err);
      const msg = err instanceof Error ? err.message : 'Failed to step episode';
      setError(msg);
      toast(msg, 'error');
      setIsJudging(false);
    } finally {
      setLoading(false);
    }
  }, [episode, toast]);

  const handleStep = useCallback(() => handleStepWithAction(), [handleStepWithAction]);

  // Feature 5: Auto-play hook
  useAutoPlay(
    handleStep,
    autoSpeed,
    autoPlaying,
    episode?.done ?? true,
    loading,
  );

  // Stop auto-play when episode ends
  useEffect(() => {
    if (episode?.done) setAutoPlaying(false);
  }, [episode?.done]);

  // Feature 3: Keyboard shortcuts
  const { showHelp, setShowHelp } = useKeyboardShortcuts({
    onStep: episode && !episode.done ? handleStep : undefined,
    onRestart: () => {
      if (episode) handleStart({ seed: episode.seed, template: episode.template, difficulty: episode.difficulty });
    },
    onAutoPlay: () => {
      if (episode && !episode.done) setAutoPlaying((p) => !p);
    },
    onToggleEditor: () => setShowEditor((p) => !p),
    disabled: loading,
  });

  // Feature 11: Submit from protocol editor
  const handleEditorSubmit = useCallback((action: ScientistAction) => {
    setShowEditor(false);
    handleStepWithAction(action);
  }, [handleStepWithAction]);

  // ─── PRE-GAME SCREEN ───────────────────────────────────────────────

  if (!episode) {
    return (
      <div className="mx-auto max-w-screen-2xl p-4">
        <ShortcutsOverlay show={showHelp} onClose={() => setShowHelp(false)} />

        <div className="flex flex-col items-center justify-center py-16">
          <motion.div
            className="mb-8 flex items-end justify-center gap-8"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <AnimatedCharacter role="scientist" emotion="idle" isActive={false} size="xl" showAura={false} showEmoji={false} />
            <motion.div className="mb-12 flex flex-col items-center" initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ delay: 0.3, type: 'spring' }}>
              <span className="text-2xl font-black text-muted-foreground/20">VS</span>
            </motion.div>
            <AnimatedCharacter role="lab_manager" emotion="idle" isActive={false} size="xl" showAura={false} showEmoji={false} />
            <motion.div className="mb-12 flex flex-col items-center" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.5 }}>
              <span className="text-xs font-bold text-muted-foreground/30">then</span>
            </motion.div>
            <motion.div className="flex flex-col items-center" initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.6, type: 'spring' }}>
              <AnimatedCharacter role="judge" emotion="idle" isActive={false} size="xl" showAura={false} showEmoji={false} />
            </motion.div>
          </motion.div>

          <motion.div className="mb-8 text-center" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.4 }}>
            <h1 className="mb-2 text-2xl font-bold">Start a New Episode</h1>
            <p className="text-muted-foreground">Choose a scenario, set difficulty, and watch them negotiate</p>
            <ShortcutHint className="mt-2" />
          </motion.div>

          {error && (
            <motion.div className="mb-4 w-full max-w-sm rounded-lg border border-destructive/50 bg-destructive/10 p-3 text-sm text-destructive" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
              {error}
            </motion.div>
          )}

          <motion.div className="w-full max-w-sm" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
            <Controls onStart={handleStart} disabled={loading} episodeActive={false} />
          </motion.div>
        </div>
      </div>
    );
  }

  // ─── ACTIVE EPISODE SCREEN ─────────────────────────────────────────

  return (
    <div className="mx-auto max-w-screen-2xl p-4">
      <ShortcutsOverlay show={showHelp} onClose={() => setShowHelp(false)} />

      {/* Character Stage */}
      <AnimatePresence>
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="mb-4">
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

      {error && (
        <motion.div className="mb-4 rounded-lg border border-destructive/50 bg-destructive/10 p-3 text-sm text-destructive" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          {error}
        </motion.div>
      )}

      {/* Feature 10: Agent Thoughts (full width above panels) */}
      {!episode.done && episode.conversation.length > 0 && (
        <motion.div className="mb-4" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }}>
          <AgentThoughts
            messages={episode.conversation}
            labConstraints={episode.lab_constraints}
            protocol={episode.protocol}
          />
        </motion.div>
      )}

      {/* Three-panel layout */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-12">
        {/* Left panel */}
        <motion.div className="space-y-4 lg:col-span-3" initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.1 }}>
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

          {/* Feature 13: 3D Lab toggle */}
          <button
            onClick={() => setShow3DLab((p) => !p)}
            className="w-full rounded-lg border border-border bg-card px-3 py-2 text-xs font-medium text-muted-foreground hover:bg-muted transition-colors"
          >
            {show3DLab ? 'Hide' : 'Show'} 3D Lab View
          </button>
          <AnimatePresence>
            {show3DLab && (
              <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} exit={{ opacity: 0, height: 0 }}>
                <Suspense fallback={<div className="h-[200px] rounded-lg border border-border bg-card flex items-center justify-center text-xs text-muted-foreground">Loading 3D...</div>}>
                  <LabScene3D constraints={episode.lab_constraints} protocol={episode.protocol} />
                </Suspense>
              </motion.div>
            )}
          </AnimatePresence>

          <Controls
            onStart={handleStart}
            onStep={!episode.done ? handleStep : undefined}
            disabled={loading}
            episodeActive={true}
          />

          {/* Feature 5: Auto-play controls */}
          <AnimatePresence>
            {!episode.done && (
              <AutoPlayControls
                isPlaying={autoPlaying}
                speed={autoSpeed}
                round={episode.round}
                maxRounds={episode.max_rounds}
                done={episode.done}
                onTogglePlay={() => setAutoPlaying((p) => !p)}
                onSpeedChange={setAutoSpeed}
              />
            )}
          </AnimatePresence>

          {/* Feature 6: Live score gauges */}
          {!episode.done && (
            <LiveScoreGauges
              conversation={episode.conversation}
              protocol={episode.protocol}
              labConstraints={episode.lab_constraints}
              paper={episode.paper}
            />
          )}

          <ShortcutHint />
        </motion.div>

        {/* Center panel */}
        <motion.div className="flex flex-col lg:col-span-5" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <NegotiationLog
            messages={episode.conversation}
            className="min-h-[400px] rounded-lg border border-border bg-card"
          />

          {/* Feature 7: Protocol evolution timeline */}
          {episode.conversation.length > 0 && (
            <motion.div className="mt-4" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.4 }}>
              <ProtocolTimeline messages={episode.conversation} />
            </motion.div>
          )}

          {episode.done && episode.judge_audit && (
            <motion.div className="mt-4" initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.5 }}>
              <JudgeAuditPanel audit={episode.judge_audit} />
            </motion.div>
          )}
        </motion.div>

        {/* Right panel */}
        <motion.div className="space-y-4 lg:col-span-4" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.3 }}>
          <ProtocolPanel protocol={episode.protocol} paper={episode.paper} />
          <ScorePanel scores={episode.scores} done={episode.done} />

          {/* Feature 11: Protocol editor toggle */}
          {!episode.done && (
            <>
              <button
                onClick={() => setShowEditor((p) => !p)}
                className="w-full rounded-lg border border-primary/30 bg-primary/5 px-3 py-2 text-xs font-semibold text-primary hover:bg-primary/10 transition-colors"
              >
                {showEditor ? 'Hide' : 'Open'} Protocol Editor
                <kbd className="ml-2 rounded border border-primary/20 bg-primary/10 px-1 font-mono text-[9px]">E</kbd>
              </button>
              <AnimatePresence>
                {showEditor && (
                  <ProtocolEditor
                    episode={episode}
                    onSubmit={handleEditorSubmit}
                    disabled={loading}
                  />
                )}
              </AnimatePresence>
            </>
          )}

          {episode.done && <ReplayViewer messages={episode.conversation} />}
        </motion.div>
      </div>
    </div>
  );
}
