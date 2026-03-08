import { Suspense } from 'react';
import { Link } from 'react-router-dom';
import {
  FlaskConical,
  Play,
  BarChart3,
  Cpu,
  ArrowRight,
  FileText,
  MessageSquare,
  Scale,
  TrendingUp,
  CheckCircle2,
  AlertTriangle,
  XCircle,
} from 'lucide-react';
import TrainingResults from '@/components/TrainingResults';
import AnimatedCharacter from '@/components/AnimatedCharacter';
import MoleculeScene from '@/components/MoleculeScene';
import TiltCard from '@/components/TiltCard';
import { cn } from '@/lib/utils';
import { DEMO_CASES } from '@/lib/demo';

const SCENARIOS = [
  {
    id: 'math_reasoning',
    label: 'Math Reasoning',
    description: 'Replicate proof planning experiments with symbolic computation resources and verification constraints',
    icon: BarChart3,
    color: 'text-scientist',
    bg: 'bg-scientist/10',
    glare: 'rgba(59,130,246,0.15)',
  },
  {
    id: 'ml_benchmark',
    label: 'ML Benchmark',
    description: 'Replicate ViT fine-tuning results with GPU compute budget, seed constraints, and baseline reproduction',
    icon: Cpu,
    color: 'text-primary',
    bg: 'bg-primary/10',
    glare: 'rgba(99,102,241,0.15)',
  },
  {
    id: 'finance_trading',
    label: 'Finance Trading',
    description: 'Replicate offline trading strategy evaluation under market data access and computational budget constraints',
    icon: FlaskConical,
    color: 'text-lab-manager',
    bg: 'bg-lab-manager/10',
    glare: 'rgba(16,185,129,0.15)',
  },
];

const ROLES = [
  {
    key: 'scientist',
    name: 'Dr. Elara - The Scientist',
    tagline: 'Protects the Science',
    description: 'A brilliant researcher who proposes, revises, and asks questions to build the best replication plan without compromising scientific validity.',
    color: 'text-scientist',
    border: 'border-scientist/30',
    glare: 'rgba(59,130,246,0.1)',
  },
  {
    key: 'lab_manager',
    name: 'Takuma - The Lab Manager',
    tagline: 'Guards Feasibility',
    description: 'A pragmatic organizer who reports budget, equipment, scheduling, and staffing constraints. He ensures plans are actually executable.',
    color: 'text-lab-manager',
    border: 'border-lab-manager/30',
    glare: 'rgba(16,185,129,0.1)',
  },
  {
    key: 'judge',
    name: 'Aldric - The Judge',
    tagline: 'Delivers the Verdict',
    description: 'An impartial arbiter who scores the final protocol on rigor, feasibility, and fidelity using a deterministic rubric engine.',
    color: 'text-judge',
    border: 'border-judge/30',
    glare: 'rgba(245,158,11,0.1)',
  },
];

const FLOW = [
  {
    title: 'Start From a Paper',
    description: 'Load a paper or evidence pack, then freeze it into a seeded replication brief.',
    icon: FileText,
  },
  {
    title: 'Negotiate the Protocol',
    description: 'Scientist and Lab Manager iterate until the plan is both rigorous and feasible.',
    icon: MessageSquare,
  },
  {
    title: 'Judge Deterministically',
    description: 'The final protocol is scored on rigor, feasibility, and fidelity under a fixed rubric.',
    icon: Scale,
  },
  {
    title: 'Train the Scientist',
    description: 'The same judged environment feeds Unsloth + TRL training and fixed-seed evaluation.',
    icon: TrendingUp,
  },
];

export default function DashboardPage() {
  return (
    <div className="mx-auto max-w-screen-xl px-4 py-8">
      {/* Hero with 3D background */}
      <section className="relative mb-16 text-center">
        {/* 3D molecule background */}
        <Suspense fallback={null}>
          <MoleculeScene
            className="absolute inset-0 -top-20 -bottom-20 z-0 opacity-25"
            variant="hero"
          />
        </Suspense>

        <div className="relative z-10">
          <div className="mb-4 inline-flex items-center gap-2 rounded-full bg-primary/10 px-4 py-1.5 text-sm font-medium text-primary backdrop-blur-sm">
            <FlaskConical className="h-4 w-4" />
            OpenEnv Hackathon
          </div>
          <h1 className="mb-3 text-4xl font-bold tracking-tight">
            Replica<span className="text-primary">Lab</span>
          </h1>
          <p className="mx-auto max-w-2xl text-lg text-muted-foreground">
            Start from a paper, turn it into a constrained replication benchmark, watch the Scientist and
            Lab Manager negotiate the protocol, then train the Scientist with deterministic reward.
          </p>

          {/* Hero character lineup - all three characters */}
          <div className="mt-8 flex items-end justify-center gap-6 md:gap-12">
            <div className="flex flex-col items-center">
              <AnimatedCharacter
                role="scientist"
                emotion="idle"
                isActive
                size="xl"
                showAura
                showEmoji={false}
                showName={false}
              />
              <span className="mt-2 text-xs font-semibold text-scientist">Proposes</span>
            </div>
            <div className="mb-10 flex flex-col items-center">
              <span className="mb-1 text-xs font-bold tracking-widest text-muted-foreground">VS</span>
              <div className="h-px w-12 bg-border" />
            </div>
            <div className="flex flex-col items-center">
              <AnimatedCharacter
                role="lab_manager"
                emotion="idle"
                isActive
                size="xl"
                showAura
                showEmoji={false}
                showName={false}
              />
              <span className="mt-2 text-xs font-semibold text-lab-manager">Constrains</span>
            </div>
            <div className="mb-10 flex flex-col items-center">
              <span className="mb-1 text-xs font-bold tracking-widest text-muted-foreground/40">then</span>
              <div className="h-px w-8 bg-border/50" />
            </div>
            <div className="flex flex-col items-center">
              <AnimatedCharacter
                role="judge"
                emotion="idle"
                isActive
                size="xl"
                showAura
                showEmoji={false}
                showName={false}
              />
              <span className="mt-2 text-xs font-semibold text-judge">Judges</span>
            </div>
          </div>

          <div className="mt-8 flex items-center justify-center gap-3">
            <Link
              to="/episode?template=ml_benchmark&difficulty=medium&seed=101&demo=1&autoplay=1&demoCase=fast-agreement"
              className="inline-flex items-center gap-2 rounded-lg bg-primary px-5 py-2.5 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90 shadow-lg shadow-primary/25"
            >
              <Play className="h-4 w-4" />
              Replicate a Paper
            </Link>
            <Link
              to="/training"
              className="inline-flex items-center gap-2 rounded-lg border border-border bg-background/80 backdrop-blur-sm px-5 py-2.5 text-sm font-medium text-foreground transition-colors hover:bg-muted"
            >
              <BarChart3 className="h-4 w-4" />
              See Training Logs
            </Link>
          </div>

          <div className="mx-auto mt-8 grid max-w-4xl gap-3 text-left md:grid-cols-4">
            {FLOW.map((item) => (
              <div key={item.title} className="rounded-xl border border-border/70 bg-background/75 p-4 backdrop-blur-sm">
                <item.icon className="mb-3 h-4 w-4 text-primary" />
                <h2 className="text-sm font-semibold">{item.title}</h2>
                <p className="mt-1 text-xs text-muted-foreground">{item.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Roles with 3D tilt character cards */}
      <section className="mb-16">
        <h2 className="mb-2 text-center text-xl font-semibold">Meet the Cast</h2>
        <p className="mb-8 text-center text-sm text-muted-foreground">
          Three roles, each with their own priorities
        </p>
        <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
          {ROLES.map((role) => (
            <TiltCard
              key={role.key}
              className={cn('rounded-xl border bg-card', role.border)}
              glareColor={role.glare}
              tiltDegree={12}
            >
              <div className="p-6">
                <div className="mb-4 flex justify-center" style={{ transform: 'translateZ(30px)', transformStyle: 'preserve-3d' }}>
                  <AnimatedCharacter
                    role={role.key}
                    emotion="idle"
                    size="xl"
                    showAura={false}
                    showEmoji={false}
                    showName={false}
                  />
                </div>
                <div className="text-center" style={{ transform: 'translateZ(15px)', transformStyle: 'preserve-3d' }}>
                  <h3 className={cn('text-base font-bold', role.color)}>{role.name}</h3>
                  <p className="mb-2 text-xs font-medium text-muted-foreground">{role.tagline}</p>
                  <p className="text-sm text-muted-foreground">{role.description}</p>
                </div>
              </div>
            </TiltCard>
          ))}
        </div>
      </section>

      {/* Scenarios with 3D tilt cards */}
      <section className="mb-16">
        <h2 className="mb-2 text-center text-xl font-semibold">Scenario Families</h2>
        <p className="mb-8 text-center text-sm text-muted-foreground">
          Different scientific domains, unique constraints
        </p>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          {SCENARIOS.map((s) => (
            <Link key={s.id} to={`/episode?template=${s.id}`}>
              <TiltCard
                className="rounded-lg border border-border bg-card"
                glareColor={s.glare}
                tiltDegree={8}
              >
                <div className="p-5">
                  <div className={cn('mb-3 inline-flex rounded-lg p-2', s.bg)} style={{ transform: 'translateZ(20px)', transformStyle: 'preserve-3d' }}>
                    <s.icon className={cn('h-5 w-5', s.color)} />
                  </div>
                  <h3 className="mb-1 font-semibold">{s.label}</h3>
                  <p className="mb-3 text-sm text-muted-foreground">{s.description}</p>
                  <span className="inline-flex items-center gap-1 text-xs font-medium text-primary">
                    Try it <ArrowRight className="h-3 w-3" />
                  </span>
                </div>
              </TiltCard>
            </Link>
          ))}
        </div>
      </section>

      {/* Episode Flow */}
      <section className="mb-16">
        <h2 className="mb-2 text-center text-xl font-semibold">Demo Flow</h2>
        <p className="mb-8 text-center text-sm text-muted-foreground">
          The live demo should tell one story from source paper to trained agent
        </p>
        <div className="mx-auto flex max-w-3xl flex-col gap-0 md:flex-row md:items-start md:gap-0">
          {[
            { step: 1, title: 'Source', desc: 'Show the paper and the original experiment that must be replicated.' },
            { step: 2, title: 'Brief', desc: 'Freeze the paper into a seeded ReplicaLab task with lab constraints.' },
            { step: 3, title: 'Negotiate', desc: 'Let the Scientist and Lab Manager revise the protocol live.' },
            { step: 4, title: 'Train', desc: 'Close with the deterministic judge and the minimal Colab training path.' },
          ].map(({ step, title, desc }, i) => (
            <div key={step} className="flex flex-1 flex-col items-center text-center">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary text-sm font-bold text-primary-foreground shadow-lg shadow-primary/20">
                {step}
              </div>
              {i < 3 && (
                <div className="hidden h-0.5 w-8 bg-border md:block md:translate-y-5 md:self-auto" />
              )}
              <h3 className="mt-2 text-sm font-semibold">{title}</h3>
              <p className="mt-1 text-xs text-muted-foreground">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="mb-16">
        <h2 className="mb-2 text-center text-xl font-semibold">Live Demo Outcomes</h2>
        <p className="mb-8 text-center text-sm text-muted-foreground">
          Pick the exact story you want to show: immediate agreement, multi-round learning, or clear rejection.
        </p>
        <div className="grid gap-4 md:grid-cols-3">
          {DEMO_CASES.map((demo) => {
            const Icon =
              demo.id === 'fast-agreement'
                ? CheckCircle2
                : demo.id === 'learning-opportunity'
                  ? AlertTriangle
                  : XCircle;

            return (
              <Link
                key={demo.id}
                to={`/episode?template=ml_benchmark&difficulty=medium&seed=${demo.seed}&demo=1&autoplay=1&demoCase=${demo.id}`}
                className="rounded-xl border border-border bg-card p-5 transition-colors hover:border-primary/40 hover:bg-muted/40"
              >
                <div className="mb-3 inline-flex rounded-full bg-primary/10 p-2 text-primary">
                  <Icon className="h-4 w-4" />
                </div>
                <h3 className="text-sm font-semibold">{demo.title}</h3>
                <p className="mt-1 text-xs font-medium text-primary">{demo.subtitle}</p>
                <p className="mt-3 text-sm text-muted-foreground">{demo.summary}</p>
                <div className="mt-4 inline-flex items-center gap-1 text-xs font-medium text-primary">
                  Launch demo <ArrowRight className="h-3 w-3" />
                </div>
              </Link>
            );
          })}
        </div>
      </section>

      {/* Training Results */}
      <section id="training" className="mb-12">
        <h2 className="mb-2 text-center text-xl font-semibold">Training Results</h2>
        <p className="mb-8 text-center text-sm text-muted-foreground">
          The judged episode becomes a reproducible training signal for the Scientist policy
        </p>
        <div className="mx-auto max-w-2xl">
          <TrainingResults />
        </div>
        <div className="mt-4 text-center">
          <Link
            to="/training"
            className="inline-flex items-center gap-2 text-sm font-medium text-primary transition-colors hover:text-primary/80"
          >
            Open the detailed training page
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </section>
    </div>
  );
}
