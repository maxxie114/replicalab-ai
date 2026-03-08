import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Pencil, Send, Plus, Trash2 } from 'lucide-react';
import type { ScientistAction, EpisodeState } from '@/types';
import { cn } from '@/lib/utils';

interface ProtocolEditorProps {
  episode: EpisodeState;
  onSubmit: (action: ScientistAction) => void;
  disabled?: boolean;
  className?: string;
}

export default function ProtocolEditor({
  episode,
  onSubmit,
  disabled,
  className,
}: ProtocolEditorProps) {
  const [actionType, setActionType] = useState<'propose_protocol' | 'revise_protocol' | 'request_info' | 'accept'>('propose_protocol');
  const [sampleSize, setSampleSize] = useState(3);
  const [technique, setTechnique] = useState('');
  const [durationDays, setDurationDays] = useState(5);
  const [controls, setControls] = useState<string[]>(['baseline']);
  const [equipment, setEquipment] = useState<string[]>([]);
  const [reagents, setReagents] = useState<string[]>([]);
  const [rationale, setRationale] = useState('');
  const [questions, setQuestions] = useState<string[]>([]);
  const [newControl, setNewControl] = useState('');
  const [newQuestion, setNewQuestion] = useState('');

  // Pre-fill from current protocol if exists
  useEffect(() => {
    if (episode.protocol) {
      setSampleSize(episode.protocol.sample_size);
      setTechnique(episode.protocol.technique);
      setDurationDays(episode.protocol.duration_days);
      setControls([...episode.protocol.controls]);
      setEquipment([...episode.protocol.required_equipment]);
      setReagents([...episode.protocol.required_reagents]);
      setActionType(episode.round > 0 ? 'revise_protocol' : 'propose_protocol');
    }
  }, [episode.protocol, episode.round]);

  function handleSubmit() {
    if (actionType === 'accept') {
      onSubmit({
        action_type: 'accept',
        sample_size: 0,
        controls: [],
        technique: '',
        duration_days: 0,
        required_equipment: [],
        required_reagents: [],
        questions: [],
        rationale: '',
      });
      return;
    }

    if (actionType === 'request_info') {
      onSubmit({
        action_type: 'request_info',
        sample_size: 0,
        controls: [],
        technique: '',
        duration_days: 0,
        required_equipment: [],
        required_reagents: [],
        questions: questions.filter(Boolean),
        rationale: '',
      });
      return;
    }

    onSubmit({
      action_type: actionType,
      sample_size: sampleSize,
      controls: controls.filter(Boolean),
      technique,
      duration_days: durationDays,
      required_equipment: equipment.filter(Boolean),
      required_reagents: reagents.filter(Boolean),
      questions: [],
      rationale,
    });
  }

  const isProtocolAction = actionType === 'propose_protocol' || actionType === 'revise_protocol';
  const canSubmit = actionType === 'accept' ||
    (actionType === 'request_info' && questions.some(Boolean)) ||
    (isProtocolAction && sampleSize > 0 && technique && rationale);

  return (
    <motion.div
      className={cn('rounded-lg border border-primary/30 bg-card overflow-hidden', className)}
      initial={{ opacity: 0, height: 0 }}
      animate={{ opacity: 1, height: 'auto' }}
      exit={{ opacity: 0, height: 0 }}
    >
      <div className="border-b border-border px-4 py-2.5 flex items-center gap-2">
        <Pencil className="h-4 w-4 text-primary" />
        <span className="text-xs font-semibold">Protocol Editor</span>
        <span className="ml-auto text-[10px] text-muted-foreground">Craft your action</span>
      </div>

      <div className="p-4 space-y-3">
        {/* Action type selector */}
        <div>
          <label className="mb-1 block text-[10px] font-medium text-muted-foreground">Action Type</label>
          <div className="flex gap-1">
            {(['propose_protocol', 'revise_protocol', 'request_info', 'accept'] as const).map((t) => (
              <button
                key={t}
                onClick={() => setActionType(t)}
                className={cn(
                  'rounded-md border px-2 py-1 text-[10px] font-medium transition-colors',
                  actionType === t
                    ? 'border-primary bg-primary/10 text-primary'
                    : 'border-border text-muted-foreground hover:bg-muted',
                )}
              >
                {t.replace(/_/g, ' ')}
              </button>
            ))}
          </div>
        </div>

        <AnimatePresence mode="wait">
          {isProtocolAction && (
            <motion.div
              key="protocol-fields"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="space-y-2.5"
            >
              <div className="grid grid-cols-3 gap-2">
                <Field label="Sample Size">
                  <input
                    type="number"
                    min={1}
                    value={sampleSize}
                    onChange={(e) => setSampleSize(parseInt(e.target.value) || 0)}
                    className="w-full rounded border border-border bg-background px-2 py-1 text-xs"
                  />
                </Field>
                <Field label="Duration (days)">
                  <input
                    type="number"
                    min={1}
                    value={durationDays}
                    onChange={(e) => setDurationDays(parseInt(e.target.value) || 0)}
                    className="w-full rounded border border-border bg-background px-2 py-1 text-xs"
                  />
                </Field>
                <Field label="Technique">
                  <input
                    type="text"
                    value={technique}
                    onChange={(e) => setTechnique(e.target.value)}
                    placeholder="e.g. fine_tuning"
                    className="w-full rounded border border-border bg-background px-2 py-1 text-xs"
                  />
                </Field>
              </div>

              {/* Controls */}
              <Field label="Controls">
                <div className="flex flex-wrap gap-1 mb-1">
                  {controls.map((c, i) => (
                    <span key={i} className="inline-flex items-center gap-0.5 rounded-full bg-scientist/10 px-2 py-0.5 text-[10px] text-scientist">
                      {c}
                      <button onClick={() => setControls(controls.filter((_, j) => j !== i))}><Trash2 className="h-2.5 w-2.5" /></button>
                    </span>
                  ))}
                </div>
                <div className="flex gap-1">
                  <input
                    type="text"
                    value={newControl}
                    onChange={(e) => setNewControl(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && newControl.trim()) {
                        setControls([...controls, newControl.trim()]);
                        setNewControl('');
                      }
                    }}
                    placeholder="Add control..."
                    className="flex-1 rounded border border-border bg-background px-2 py-0.5 text-[10px]"
                  />
                  <button
                    onClick={() => {
                      if (newControl.trim()) {
                        setControls([...controls, newControl.trim()]);
                        setNewControl('');
                      }
                    }}
                    className="rounded border border-border p-0.5 text-muted-foreground hover:bg-muted"
                  >
                    <Plus className="h-3 w-3" />
                  </button>
                </div>
              </Field>

              {/* Equipment from available */}
              <Field label="Equipment (click to toggle)">
                <div className="flex flex-wrap gap-1">
                  {episode.lab_constraints.equipment_available.map((e) => (
                    <button
                      key={e}
                      onClick={() =>
                        setEquipment((prev) =>
                          prev.includes(e) ? prev.filter((x) => x !== e) : [...prev, e],
                        )
                      }
                      className={cn(
                        'rounded-full border px-2 py-0.5 text-[10px] font-medium transition-colors',
                        equipment.includes(e)
                          ? 'border-lab-manager bg-lab-manager/10 text-lab-manager'
                          : 'border-border text-muted-foreground hover:bg-muted',
                      )}
                    >
                      {e.replace(/_/g, ' ')}
                    </button>
                  ))}
                </div>
              </Field>

              {/* Reagents from available */}
              <Field label="Reagents (click to toggle)">
                <div className="flex flex-wrap gap-1">
                  {episode.lab_constraints.reagents_available.map((r) => (
                    <button
                      key={r}
                      onClick={() =>
                        setReagents((prev) =>
                          prev.includes(r) ? prev.filter((x) => x !== r) : [...prev, r],
                        )
                      }
                      className={cn(
                        'rounded-full border px-2 py-0.5 text-[10px] font-medium transition-colors',
                        reagents.includes(r)
                          ? 'border-scientist bg-scientist/10 text-scientist'
                          : 'border-border text-muted-foreground hover:bg-muted',
                      )}
                    >
                      {r.replace(/_/g, ' ')}
                    </button>
                  ))}
                </div>
              </Field>

              {/* Rationale */}
              <Field label="Rationale">
                <textarea
                  value={rationale}
                  onChange={(e) => setRationale(e.target.value)}
                  placeholder="Why this protocol? Explain your reasoning..."
                  rows={2}
                  className="w-full rounded border border-border bg-background px-2 py-1 text-xs resize-none"
                />
              </Field>
            </motion.div>
          )}

          {actionType === 'request_info' && (
            <motion.div
              key="info-fields"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <Field label="Questions">
                {questions.map((q, i) => (
                  <div key={i} className="flex gap-1 mb-1">
                    <input
                      type="text"
                      value={q}
                      onChange={(e) => {
                        const next = [...questions];
                        next[i] = e.target.value;
                        setQuestions(next);
                      }}
                      className="flex-1 rounded border border-border bg-background px-2 py-0.5 text-xs"
                    />
                    <button onClick={() => setQuestions(questions.filter((_, j) => j !== i))} className="text-muted-foreground hover:text-destructive">
                      <Trash2 className="h-3 w-3" />
                    </button>
                  </div>
                ))}
                <div className="flex gap-1">
                  <input
                    type="text"
                    value={newQuestion}
                    onChange={(e) => setNewQuestion(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && newQuestion.trim()) {
                        setQuestions([...questions, newQuestion.trim()]);
                        setNewQuestion('');
                      }
                    }}
                    placeholder="Ask a question..."
                    className="flex-1 rounded border border-border bg-background px-2 py-0.5 text-xs"
                  />
                  <button
                    onClick={() => {
                      if (newQuestion.trim()) {
                        setQuestions([...questions, newQuestion.trim()]);
                        setNewQuestion('');
                      }
                    }}
                    className="rounded border border-border p-0.5 text-muted-foreground hover:bg-muted"
                  >
                    <Plus className="h-3 w-3" />
                  </button>
                </div>
              </Field>
            </motion.div>
          )}

          {actionType === 'accept' && (
            <motion.div
              key="accept-msg"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="rounded-md bg-lab-manager/10 border border-lab-manager/30 p-3 text-center"
            >
              <p className="text-sm font-medium text-lab-manager">Accept the current protocol</p>
              <p className="text-xs text-muted-foreground">The judge will evaluate the final agreement</p>
            </motion.div>
          )}
        </AnimatePresence>

        <button
          onClick={handleSubmit}
          disabled={disabled || !canSubmit}
          className="flex w-full items-center justify-center gap-1.5 rounded-md bg-primary px-3 py-2 text-xs font-medium text-primary-foreground transition-colors hover:bg-primary/90 disabled:opacity-50"
        >
          <Send className="h-3.5 w-3.5" />
          Submit Action
        </button>
      </div>
    </motion.div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <label className="mb-0.5 block text-[10px] font-medium text-muted-foreground">{label}</label>
      {children}
    </div>
  );
}
