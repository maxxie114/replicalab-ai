import type { ReactNode } from 'react';
import { motion } from 'framer-motion';
import { Bot, BrainCircuit, CheckCircle2, FlaskConical, ShieldAlert } from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
} from 'recharts';
import { CURRENT_RUNTIME_MODEL_STATUS, POLICY_COMPARE } from '@/data/trainingArtifacts';
import { cn, formatReward, formatScore } from '@/lib/utils';

const measuredPolicies = POLICY_COMPARE.filter((policy) => policy.averageReward !== null);
const chartRows = measuredPolicies.map((policy) => ({
  label: policy.label,
  reward: Number((policy.averageReward ?? 0).toFixed(2)),
  agreement: Number(((policy.agreementRate ?? 0) * 100).toFixed(1)),
  invalid: Number(((policy.invalidRate ?? 0) * 100).toFixed(1)),
}));

export default function PolicyComparePage() {
  return (
    <div className="mx-auto max-w-screen-xl px-4 py-8">
      <motion.div
        className="mb-8 text-center"
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="mb-3 inline-flex items-center gap-2 rounded-full bg-primary/10 px-4 py-1.5 text-sm font-medium text-primary">
          <BrainCircuit className="h-4 w-4" />
          Baseline Vs Trained Vs Oracle
        </div>
        <h1 className="mb-2 text-3xl font-bold tracking-tight">Policy Runtime And Results</h1>
        <p className="mx-auto max-w-3xl text-muted-foreground">
          This page separates three things that were easy to conflate in the demo: the live deterministic baseline
          runtime, the trained Scientist artifact, and the planned oracle-assisted V2 path.
        </p>
      </motion.div>

      <motion.div
        className="mb-6 rounded-xl border border-judge/30 bg-judge/5 p-5"
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.05 }}
      >
        <div className="mb-2 flex items-center gap-2 text-sm font-semibold text-judge">
          <ShieldAlert className="h-4 w-4" />
          Are we even running a model right now?
        </div>
        <p className="text-sm text-muted-foreground">{CURRENT_RUNTIME_MODEL_STATUS.note}</p>
        <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          <RuntimeFlag
            label="Compare page"
            value={CURRENT_RUNTIME_MODEL_STATUS.comparePageUsesLiveModel ? 'Model-backed' : 'Deterministic runtime'}
            positive={CURRENT_RUNTIME_MODEL_STATUS.comparePageUsesLiveModel}
          />
          <RuntimeFlag
            label="Episode page"
            value={CURRENT_RUNTIME_MODEL_STATUS.episodePageUsesLiveModel ? 'Model-backed' : 'Deterministic runtime'}
            positive={CURRENT_RUNTIME_MODEL_STATUS.episodePageUsesLiveModel}
          />
          <RuntimeFlag
            label="Oracle path"
            value={CURRENT_RUNTIME_MODEL_STATUS.backendUsesOracle ? 'Enabled' : 'Disabled in public runtime'}
            positive={CURRENT_RUNTIME_MODEL_STATUS.backendUsesOracle}
          />
          <RuntimeFlag
            label="Judge"
            value={CURRENT_RUNTIME_MODEL_STATUS.backendUsesDeterministicJudge ? 'Deterministic' : 'Model-scored'}
            positive={CURRENT_RUNTIME_MODEL_STATUS.backendUsesDeterministicJudge}
          />
        </div>
      </motion.div>

      <motion.div
        className="mb-6 grid gap-4 lg:grid-cols-3"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        {POLICY_COMPARE.map((policy) => (
          <PolicyCard key={policy.id} policy={policy} />
        ))}
      </motion.div>

      <motion.div
        className="mb-6 rounded-xl border border-border bg-card p-5"
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.15 }}
      >
        <div className="mb-4">
          <h2 className="text-base font-semibold">Measured policies only</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            The chart below only includes policy variants that already have actual numeric results. The oracle lane is
            intentionally excluded until a real evaluation artifact exists.
          </p>
        </div>
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartRows}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
              <XAxis dataKey="label" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Legend wrapperStyle={{ fontSize: '12px' }} />
              <Bar dataKey="reward" fill="var(--color-primary)" radius={[6, 6, 0, 0]} name="Avg reward" />
              <Bar dataKey="agreement" fill="var(--color-lab-manager)" radius={[6, 6, 0, 0]} name="Agreement %" />
              <Bar dataKey="invalid" fill="var(--color-destructive)" radius={[6, 6, 0, 0]} name="Invalid %" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </motion.div>

      <motion.div
        className="rounded-xl border border-border bg-card p-5"
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <h2 className="mb-4 text-base font-semibold">What each lane actually means</h2>
        <div className="grid gap-4 lg:grid-cols-3">
          <MeaningCard
            icon={<FlaskConical className="h-4 w-4" />}
            title="Baseline"
            body="This is the current live runtime. It uses the default Scientist action builder plus the deterministic Lab Manager and Judge. It is stable, but it is not a trained LLM policy."
          />
          <MeaningCard
            icon={<Bot className="h-4 w-4" />}
            title="Trained"
            body="This lane uses the artifact-backed Scientist training results. The adapter exists and was evaluated, but it still loses badly to the deterministic baseline on hold-out seeds."
          />
          <MeaningCard
            icon={<CheckCircle2 className="h-4 w-4" />}
            title="Oracle"
            body="This is the planned Anthropic-assisted V2 lane. The code path exists, but the public app is not currently mounting it and there is no benchmark result we should claim yet."
          />
        </div>
      </motion.div>
    </div>
  );
}

function RuntimeFlag({
  label,
  value,
  positive,
}: {
  label: string;
  value: string;
  positive: boolean;
}) {
  return (
    <div className="rounded-lg border border-border bg-background px-3 py-3">
      <div className="text-xs font-medium text-muted-foreground">{label}</div>
      <div className={cn('mt-1 text-sm font-semibold', positive ? 'text-lab-manager' : 'text-judge')}>
        {value}
      </div>
    </div>
  );
}

function PolicyCard({
  policy,
}: {
  policy: (typeof POLICY_COMPARE)[number];
}) {
  const tone =
    policy.status === 'live'
      ? 'border-lab-manager/30'
      : policy.status === 'artifact'
        ? 'border-judge/30'
        : 'border-border';
  const badgeTone =
    policy.status === 'live'
      ? 'bg-lab-manager/10 text-lab-manager'
      : policy.status === 'artifact'
        ? 'bg-judge/10 text-judge'
        : 'bg-muted text-muted-foreground';

  return (
    <div className={cn('rounded-xl border bg-card p-5', tone)}>
      <div className="mb-3 flex items-start justify-between gap-3">
        <div>
          <h2 className="text-base font-semibold">{policy.label}</h2>
          <p className="mt-1 text-xs text-muted-foreground">{policy.source}</p>
        </div>
        <span className={cn('rounded-full px-2 py-1 text-[11px] font-medium', badgeTone)}>
          {policy.status}
        </span>
      </div>

      <div className="mb-4 grid grid-cols-2 gap-2">
        <MetricTile label="Avg reward" value={policy.averageReward === null ? 'Not run' : formatReward(policy.averageReward)} />
        <MetricTile label="Agreement" value={policy.agreementRate === null ? 'Not run' : formatScore(policy.agreementRate)} />
        <MetricTile label="Avg rounds" value={policy.averageRounds === null ? 'Not run' : policy.averageRounds.toFixed(1)} />
        <MetricTile label="Invalid rate" value={policy.invalidRate === null ? 'Not run' : formatScore(policy.invalidRate)} />
      </div>

      <div className="space-y-2 text-xs text-muted-foreground">
        <div><span className="font-semibold text-foreground">Scientist:</span> {policy.scientistMode}</div>
        <div><span className="font-semibold text-foreground">Lab Manager:</span> {policy.labManagerMode}</div>
        <div><span className="font-semibold text-foreground">Judge:</span> {policy.judgeMode}</div>
      </div>

      <p className="mt-4 rounded-lg border border-border bg-muted/30 px-3 py-3 text-xs text-muted-foreground">
        {policy.summary}
      </p>
    </div>
  );
}

function MetricTile({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-border bg-muted/30 px-3 py-2">
      <div className="text-[11px] text-muted-foreground">{label}</div>
      <div className="mt-1 text-sm font-semibold">{value}</div>
    </div>
  );
}

function MeaningCard({
  icon,
  title,
  body,
}: {
  icon: ReactNode;
  title: string;
  body: string;
}) {
  return (
    <div className="rounded-lg border border-border bg-muted/20 p-4">
      <div className="mb-2 flex items-center gap-2 text-sm font-semibold">
        {icon}
        {title}
      </div>
      <p className="text-sm text-muted-foreground">{body}</p>
    </div>
  );
}
