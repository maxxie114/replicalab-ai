import { motion } from 'framer-motion';
import { GitCompareArrows } from 'lucide-react';
import EpisodeComparison from '@/components/EpisodeComparison';

export default function ComparePage() {
  return (
    <div className="mx-auto max-w-screen-xl px-4 py-8">
      <motion.div
        className="mb-8 text-center"
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="mb-3 inline-flex items-center gap-2 rounded-full bg-primary/10 px-4 py-1.5 text-sm font-medium text-primary">
          <GitCompareArrows className="h-4 w-4" />
          Evaluation Bench
        </div>
        <h1 className="mb-2 text-3xl font-bold tracking-tight">Seeded Benchmark Comparison</h1>
        <p className="mx-auto max-w-lg text-muted-foreground">
          Use the same frontend to replay fixed benchmark cases across domains or difficulty levels.
          This page is the evaluation bench for demo runs, while the training panel holds the baseline-vs-trained story.
        </p>
      </motion.div>

      <motion.div
        className="mb-6 grid gap-3 md:grid-cols-3"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <div className="rounded-lg border border-border bg-card p-4">
          <h2 className="text-sm font-semibold">Fixed seeds</h2>
          <p className="mt-1 text-xs text-muted-foreground">Replay the same benchmark cases without changing the underlying task.</p>
        </div>
        <div className="rounded-lg border border-border bg-card p-4">
          <h2 className="text-sm font-semibold">Same backend contract</h2>
          <p className="mt-1 text-xs text-muted-foreground">The UI uses the same reset and step endpoints as the live demo episode page.</p>
        </div>
        <div className="rounded-lg border border-border bg-card p-4">
          <h2 className="text-sm font-semibold">Judge-comparable</h2>
          <p className="mt-1 text-xs text-muted-foreground">Rewards and verdicts stay grounded in the deterministic ReplicaLab rubric.</p>
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <EpisodeComparison />
      </motion.div>
    </div>
  );
}
