import type { ReactNode } from 'react';
import { motion } from 'framer-motion';
import {
  BrainCircuit,
  CheckCircle2,
  FileCode2,
  FlaskConical,
  Gauge,
  GraduationCap,
  AlertTriangle,
  Wrench,
  TerminalSquare,
} from 'lucide-react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  BarChart,
  Bar,
} from 'recharts';
import {
  HOLDOUT_COMPARE,
  LAB_MANAGER_PREVIEW_ARTIFACT,
  LIVE_CHECKPOINTS,
  LOCAL_BASELINE_SUMMARY,
  SCIENTIST_PREVIEW_ARTIFACT,
  TRAINING_ASSESSMENT,
  TRAINING_LOG_ROWS,
} from '@/data/trainingArtifacts';
import { cn, formatReward, formatScore } from '@/lib/utils';

const compareBars = [
  {
    metric: 'Avg reward',
    baseline: HOLDOUT_COMPARE.summary.baseline_avg_reward,
    trained: HOLDOUT_COMPARE.summary.trained_avg_reward,
  },
  {
    metric: 'Agreement %',
    baseline: HOLDOUT_COMPARE.summary.baseline_agreement_rate * 100,
    trained: HOLDOUT_COMPARE.summary.trained_agreement_rate * 100,
  },
  {
    metric: 'Invalid %',
    baseline: HOLDOUT_COMPARE.summary.baseline_invalid_rate * 100,
    trained: HOLDOUT_COMPARE.summary.trained_invalid_rate * 100,
  },
  {
    metric: 'Avg rounds',
    baseline: HOLDOUT_COMPARE.summary.baseline_avg_rounds,
    trained: HOLDOUT_COMPARE.summary.trained_avg_rounds,
  },
];

const checkpointChart = LIVE_CHECKPOINTS.map((checkpoint) => ({
  label: checkpoint.label,
  reward: Number(checkpoint.averageReward.toFixed(3)),
  agreementPercent: Number((checkpoint.agreementRate * 100).toFixed(1)),
  rounds: Number(checkpoint.averageRounds.toFixed(2)),
}));

export default function TrainingPage() {
  const latestCheckpoint = LIVE_CHECKPOINTS[LIVE_CHECKPOINTS.length - 1];

  return (
    <div className="mx-auto max-w-screen-xl px-4 py-8">
      <motion.div
        className="mb-8 text-center"
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="mb-3 inline-flex items-center gap-2 rounded-full bg-primary/10 px-4 py-1.5 text-sm font-medium text-primary">
          <GraduationCap className="h-4 w-4" />
          Training Logs And Analysis
        </div>
        <h1 className="mb-2 text-3xl font-bold tracking-tight">Scientist And Lab Manager Training Status</h1>
        <p className="mx-auto max-w-3xl text-muted-foreground">
          This page is backed by the real ReplicaLab training artifacts already generated in the repo. It shows what
          the training stack achieved, where it is still failing, and whether more training is needed before claiming
          the agents are actually better.
        </p>
      </motion.div>

      <motion.div
        className="mb-6 grid gap-4 lg:grid-cols-4"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.05 }}
      >
        <StatusCard
          icon={<FileCode2 className="h-4 w-4" />}
          title="Scientist preview"
          value={`${SCIENTIST_PREVIEW_ARTIFACT.datasetSize} prompts`}
          detail={`${SCIENTIST_PREVIEW_ARTIFACT.modelName} · max steps ${SCIENTIST_PREVIEW_ARTIFACT.config.maxSteps}`}
        />
        <StatusCard
          icon={<FlaskConical className="h-4 w-4" />}
          title="Lab Manager preview"
          value={`${LAB_MANAGER_PREVIEW_ARTIFACT.datasetSize} samples`}
          detail={`${LAB_MANAGER_PREVIEW_ARTIFACT.modelName} · ${LAB_MANAGER_PREVIEW_ARTIFACT.config.numTrainEpochs} epoch preview`}
        />
        <StatusCard
          icon={<Gauge className="h-4 w-4" />}
          title="Latest live RL checkpoint"
          value={formatReward(latestCheckpoint.averageReward)}
          detail={`${formatScore(latestCheckpoint.agreementRate)} agreement at artifact step ${latestCheckpoint.artifactStep}`}
        />
        <StatusCard
          icon={<AlertTriangle className="h-4 w-4" />}
          title="Do we need more training?"
          value="Yes"
          detail="Hold-out compare still favors baseline."
          tone="warn"
        />
      </motion.div>

      <motion.div
        className="mb-6 grid gap-4 lg:grid-cols-2"
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <ChartCard
          title="Live RL checkpoint progression"
          subtitle="Real checkpoint summaries from the ART/OpenEnv scientist run."
        >
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={checkpointChart}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                <XAxis dataKey="label" tick={{ fontSize: 11 }} />
                <YAxis yAxisId="left" tick={{ fontSize: 11 }} />
                <YAxis
                  yAxisId="right"
                  orientation="right"
                  tick={{ fontSize: 11 }}
                  tickFormatter={(value) => `${value}%`}
                />
                <Tooltip />
                <Legend wrapperStyle={{ fontSize: '12px' }} />
                <Line yAxisId="left" type="monotone" dataKey="reward" stroke="var(--color-primary)" strokeWidth={2.5} name="Avg reward" />
                <Line yAxisId="right" type="monotone" dataKey="agreementPercent" stroke="var(--color-lab-manager)" strokeWidth={2.5} name="Agreement %" />
                <Line yAxisId="left" type="monotone" dataKey="rounds" stroke="var(--color-judge)" strokeWidth={2} name="Avg rounds" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </ChartCard>

        <ChartCard
          title="Hold-out compare"
          subtitle="Real seeded comparison between the deterministic baseline and the current trained scientist."
        >
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={compareBars}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                <XAxis dataKey="metric" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Legend wrapperStyle={{ fontSize: '12px' }} />
                <Bar dataKey="baseline" fill="var(--color-lab-manager)" radius={[6, 6, 0, 0]} name="Baseline" />
                <Bar dataKey="trained" fill="var(--color-destructive)" radius={[6, 6, 0, 0]} name="Trained" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </ChartCard>
      </motion.div>

      <motion.div
        className="mb-6 grid gap-4 lg:grid-cols-[1.35fr_1fr]"
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.16 }}
      >
        <div className="rounded-xl border border-border bg-card p-5">
          <div className="mb-4 flex items-center gap-2">
            <TerminalSquare className="h-4 w-4 text-primary" />
            <h2 className="text-base font-semibold">Training log highlights</h2>
          </div>
          <div className="space-y-3">
            {TRAINING_LOG_ROWS.map((row) => (
              <div key={row.label} className="rounded-lg border border-border bg-muted/30 p-3">
                <div className="flex flex-wrap items-center gap-2 text-[11px] font-medium">
                  <span className="rounded-full bg-background px-2 py-1 text-primary">step {row.trainingStep}</span>
                  <span className="rounded-full bg-background px-2 py-1 text-primary">seed {row.seed}</span>
                  <span className={cn(
                    'rounded-full px-2 py-1',
                    row.verdict === 'accept' ? 'bg-lab-manager/10 text-lab-manager' : 'bg-destructive/10 text-destructive',
                  )}>
                    {row.verdict ?? 'no verdict'}
                  </span>
                </div>
                <div className="mt-2 font-medium">{row.paperTitle}</div>
                <div className="mt-2 grid gap-2 text-xs text-muted-foreground sm:grid-cols-4">
                  <span>reward {formatReward(row.reward)}</span>
                  <span>rounds {row.roundsUsed}</span>
                  <span>invalid {row.invalidActionCount}</span>
                  <span>parse {row.parseErrorCount}</span>
                </div>
                <p className="mt-2 text-xs text-muted-foreground">{row.note}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="space-y-4">
          <SummaryCard
            title="What we achieved"
            icon={<CheckCircle2 className="h-4 w-4" />}
            items={TRAINING_ASSESSMENT.achieved}
            tone="good"
          />
          <SummaryCard
            title="Why the current model still fails"
            icon={<BrainCircuit className="h-4 w-4" />}
            items={TRAINING_ASSESSMENT.gaps}
            tone="warn"
          />
          <SummaryCard
            title="What to improve next"
            icon={<Wrench className="h-4 w-4" />}
            items={TRAINING_ASSESSMENT.improvements}
            tone="neutral"
          />
        </div>
      </motion.div>

      <motion.div
        className="grid gap-4 lg:grid-cols-3"
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.22 }}
      >
        <InfoPanel
          title="Local deterministic baseline"
          lines={[
            `${LOCAL_BASELINE_SUMMARY.episodeCount} episodes across all three scenario families`,
            `Average reward ${formatReward(LOCAL_BASELINE_SUMMARY.averageReward)}`,
            `Agreement ${formatScore(LOCAL_BASELINE_SUMMARY.agreementRate)}`,
            `Average rounds ${LOCAL_BASELINE_SUMMARY.averageRounds.toFixed(1)}`,
          ]}
        />
        <InfoPanel
          title="Scientist run config"
          lines={[
            SCIENTIST_PREVIEW_ARTIFACT.modelName,
            `LoRA rank ${SCIENTIST_PREVIEW_ARTIFACT.config.loraRank}`,
            `Max seq length ${SCIENTIST_PREVIEW_ARTIFACT.config.maxSeqLength}`,
            `Learning rate ${SCIENTIST_PREVIEW_ARTIFACT.config.learningRate}`,
          ]}
        />
        <InfoPanel
          title="Lab Manager status"
          lines={[
            `Preview dataset ${LAB_MANAGER_PREVIEW_ARTIFACT.datasetSize} samples`,
            `Evidence pack ${LAB_MANAGER_PREVIEW_ARTIFACT.evidencePackVersion}`,
            'Preview artifact exists, but no live evaluated SFT adapter is shown in the demo yet',
            'Next step is a real trained-plus-evaluated Lab Manager run',
          ]}
        />
      </motion.div>
    </div>
  );
}

function StatusCard({
  icon,
  title,
  value,
  detail,
  tone = 'neutral',
}: {
  icon: ReactNode;
  title: string;
  value: string;
  detail: string;
  tone?: 'neutral' | 'warn';
}) {
  return (
    <div className={cn(
      'rounded-xl border bg-card p-4',
      tone === 'warn' ? 'border-judge/30' : 'border-border',
    )}>
      <div className="mb-2 flex items-center gap-2 text-sm font-medium text-muted-foreground">
        {icon}
        {title}
      </div>
      <div className={cn('text-2xl font-bold', tone === 'warn' ? 'text-judge' : 'text-foreground')}>
        {value}
      </div>
      <p className="mt-1 text-sm text-muted-foreground">{detail}</p>
    </div>
  );
}

function ChartCard({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle: string;
  children: ReactNode;
}) {
  return (
    <div className="rounded-xl border border-border bg-card p-5">
      <h2 className="text-base font-semibold">{title}</h2>
      <p className="mt-1 text-sm text-muted-foreground">{subtitle}</p>
      <div className="mt-4">{children}</div>
    </div>
  );
}

function SummaryCard({
  title,
  icon,
  items,
  tone,
}: {
  title: string;
  icon: ReactNode;
  items: string[];
  tone: 'good' | 'warn' | 'neutral';
}) {
  return (
    <div className={cn(
      'rounded-xl border bg-card p-4',
      tone === 'good' && 'border-lab-manager/30',
      tone === 'warn' && 'border-judge/30',
      tone === 'neutral' && 'border-border',
    )}>
      <div className="mb-3 flex items-center gap-2 text-sm font-semibold">
        {icon}
        {title}
      </div>
      <div className="space-y-2">
        {items.map((item) => (
          <div key={item} className="rounded-lg border border-border bg-muted/30 px-3 py-2 text-xs text-muted-foreground">
            {item}
          </div>
        ))}
      </div>
    </div>
  );
}

function InfoPanel({ title, lines }: { title: string; lines: string[] }) {
  return (
    <div className="rounded-xl border border-border bg-card p-4">
      <h2 className="text-sm font-semibold">{title}</h2>
      <div className="mt-3 space-y-2">
        {lines.map((line) => (
          <div key={line} className="rounded-lg border border-border bg-muted/30 px-3 py-2 text-xs text-muted-foreground">
            {line}
          </div>
        ))}
      </div>
    </div>
  );
}
