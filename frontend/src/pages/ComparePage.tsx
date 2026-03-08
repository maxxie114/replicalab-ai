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
          Side-by-Side
        </div>
        <h1 className="mb-2 text-3xl font-bold tracking-tight">Episode Comparison</h1>
        <p className="mx-auto max-w-lg text-muted-foreground">
          Run multiple episodes with different scenarios, difficulties, and seeds —
          then compare outcomes side by side.
        </p>
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
