import { Suspense } from 'react';
import { Link } from 'react-router-dom';
import {
  FlaskConical,
  Play,
  BarChart3,
  Cpu,
  ArrowRight,
} from 'lucide-react';
import TrainingResults from '@/components/TrainingResults';
import AnimatedCharacter from '@/components/AnimatedCharacter';
import MoleculeScene from '@/components/MoleculeScene';
import TiltCard from '@/components/TiltCard';
import { cn } from '@/lib/utils';

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
    name: 'Dr. Elara — The Scientist',
    tagline: 'Protects the Science',
    description: 'A brilliant researcher who proposes, revises, and asks questions to build the best replication plan without compromising scientific validity.',
    color: 'text-scientist',
    border: 'border-scientist/30',
    glare: 'rgba(59,130,246,0.1)',
  },
  {
    key: 'lab_manager',
    name: 'Takuma — The Lab Manager',
    tagline: 'Guards Feasibility',
    description: 'A pragmatic organizer who reports budget, equipment, scheduling, and staffing constraints. He ensures plans are actually executable.',
    color: 'text-lab-manager',
    border: 'border-lab-manager/30',
    glare: 'rgba(16,185,129,0.1)',
  },
  {
    key: 'judge',
    name: 'Aldric — The Judge',
    tagline: 'Delivers the Verdict',
    description: 'An impartial arbiter who scores the final protocol on rigor, feasibility, and fidelity using a deterministic rubric engine.',
    color: 'text-judge',
    border: 'border-judge/30',
    glare: 'rgba(245,158,11,0.1)',
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
            A multi-agent ML replication environment where a Scientist and Lab Manager
            negotiate how to reproduce benchmark results under real compute constraints.
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
              />
              <span className="mt-2 text-xs font-semibold text-judge">Judges</span>
            </div>
          </div>

          <div className="mt-8 flex items-center justify-center gap-3">
            <Link
              to="/episode"
              className="inline-flex items-center gap-2 rounded-lg bg-primary px-5 py-2.5 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90 shadow-lg shadow-primary/25"
            >
              <Play className="h-4 w-4" />
              Run Episode
            </Link>
            <a
              href="#training"
              className="inline-flex items-center gap-2 rounded-lg border border-border bg-background/80 backdrop-blur-sm px-5 py-2.5 text-sm font-medium text-foreground transition-colors hover:bg-muted"
            >
              <BarChart3 className="h-4 w-4" />
              Training Results
            </a>
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
        <h2 className="mb-2 text-center text-xl font-semibold">How It Works</h2>
        <p className="mb-8 text-center text-sm text-muted-foreground">
          Each episode follows this cycle
        </p>
        <div className="mx-auto flex max-w-3xl flex-col gap-0 md:flex-row md:items-start md:gap-0">
          {[
            { step: 1, title: 'Reset', desc: 'Generate a paper and lab with constraints' },
            { step: 2, title: 'Negotiate', desc: 'Scientist and Lab Manager exchange proposals' },
            { step: 3, title: 'Judge', desc: 'Score the plan on rigor, feasibility, fidelity' },
            { step: 4, title: 'Learn', desc: 'RL training improves the Scientist over time' },
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

      {/* Training Results */}
      <section id="training" className="mb-12">
        <h2 className="mb-2 text-center text-xl font-semibold">Training Results</h2>
        <p className="mb-8 text-center text-sm text-muted-foreground">
          Dr. Elara improves through reinforcement learning
        </p>
        <div className="mx-auto max-w-2xl">
          <TrainingResults />
        </div>
      </section>
    </div>
  );
}
