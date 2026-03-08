import { Suspense, useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Float, RoundedBox, MeshDistortMaterial, Sphere } from '@react-three/drei';
import * as THREE from 'three';
import type { LabConstraints, Protocol } from '@/types';
import { cn } from '@/lib/utils';

interface LabScene3DProps {
  constraints: LabConstraints;
  protocol: Protocol | null;
  className?: string;
}

function LabBench() {
  return (
    <group position={[0, -1.2, 0]}>
      {/* Table surface */}
      <RoundedBox args={[5, 0.15, 2.5]} radius={0.05} position={[0, 0, 0]}>
        <meshStandardMaterial color="#475569" roughness={0.3} metalness={0.6} />
      </RoundedBox>
      {/* Table legs */}
      {[[-2.2, -0.6, -1], [2.2, -0.6, -1], [-2.2, -0.6, 1], [2.2, -0.6, 1]].map((pos, i) => (
        <RoundedBox key={i} args={[0.12, 1.2, 0.12]} radius={0.02} position={pos as [number, number, number]}>
          <meshStandardMaterial color="#334155" roughness={0.5} metalness={0.5} />
        </RoundedBox>
      ))}
    </group>
  );
}

function Equipment({ name, position }: { name: string; position: [number, number, number] }) {
  const meshRef = useRef<THREE.Mesh>(null);
  const color = useMemo(() => {
    const colors: Record<string, string> = {
      gpu_a100: '#6366f1',
      gpu_a6000: '#818cf8',
      wandb_logger: '#10b981',
      docker_env: '#3b82f6',
    };
    return colors[name] || '#94a3b8';
  }, [name]);

  return (
    <Float speed={2} rotationIntensity={0.3} floatIntensity={0.5}>
      <group position={position}>
        <RoundedBox ref={meshRef} args={[0.5, 0.6, 0.4]} radius={0.05}>
          <meshStandardMaterial color={color} roughness={0.2} metalness={0.8} />
        </RoundedBox>
        <pointLight position={[0, 0.5, 0]} color={color} intensity={0.5} distance={2} />
      </group>
    </Float>
  );
}

function Reagent({ name: _name, position }: { name: string; position: [number, number, number] }) {
  return (
    <Float speed={3} rotationIntensity={0.5} floatIntensity={0.3}>
      <group position={position}>
        {/* Flask shape */}
        <Sphere args={[0.15, 16, 16]} position={[0, 0, 0]}>
          <MeshDistortMaterial
            color="#34d399"
            speed={2}
            distort={0.2}
            roughness={0.1}
            metalness={0.3}
            transparent
            opacity={0.7}
          />
        </Sphere>
        {/* Neck */}
        <mesh position={[0, 0.2, 0]}>
          <cylinderGeometry args={[0.04, 0.08, 0.15, 8]} />
          <meshStandardMaterial color="#34d399" transparent opacity={0.5} />
        </mesh>
      </group>
    </Float>
  );
}

function BudgetIndicator({ budget, budgetRemaining, position }: { budget: number; budgetRemaining: number; position: [number, number, number] }) {
  const ratio = budget > 0 ? budgetRemaining / budget : 0;
  const color = ratio > 0.5 ? '#10b981' : ratio > 0.2 ? '#f59e0b' : '#ef4444';

  return (
    <group position={position}>
      {/* Background bar */}
      <RoundedBox args={[1.5, 0.12, 0.08]} radius={0.03} position={[0, 0, 0]}>
        <meshStandardMaterial color="#1e293b" roughness={0.8} />
      </RoundedBox>
      {/* Fill bar */}
      <RoundedBox args={[1.5 * ratio, 0.12, 0.1]} radius={0.03} position={[(1.5 * ratio - 1.5) / 2, 0, 0.02]}>
        <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.3} roughness={0.3} />
      </RoundedBox>
      {/* $ glow */}
      <pointLight position={[0, 0.3, 0.2]} color={color} intensity={0.8} distance={1.5} />
    </group>
  );
}

function SceneContent({ constraints, protocol: _protocol }: { constraints: LabConstraints; protocol: Protocol | null }) {
  const groupRef = useRef<THREE.Group>(null);

  useFrame(({ clock }) => {
    if (groupRef.current) {
      groupRef.current.rotation.y = Math.sin(clock.getElapsedTime() * 0.15) * 0.1;
    }
  });

  const equipPositions: [number, number, number][] = [
    [-1.5, -0.5, 0],
    [-0.5, -0.5, 0],
    [0.5, -0.5, 0],
    [1.5, -0.5, 0],
  ];

  const reagentPositions: [number, number, number][] = [
    [-1.2, -0.3, 0.8],
    [-0.4, -0.3, 0.8],
    [0.4, -0.3, 0.8],
    [1.2, -0.3, 0.8],
  ];

  return (
    <group ref={groupRef}>
      <LabBench />

      {/* Equipment items */}
      {constraints.equipment_available.slice(0, 4).map((eq, i) => (
        <Equipment key={eq} name={eq} position={equipPositions[i] || equipPositions[0]} />
      ))}

      {/* Reagent flasks */}
      {constraints.reagents_available.slice(0, 4).map((rg, i) => (
        <Reagent key={rg} name={rg} position={reagentPositions[i] || reagentPositions[0]} />
      ))}

      {/* Budget bar floating above */}
      <BudgetIndicator
        budget={constraints.budget}
        budgetRemaining={constraints.budget_remaining}
        position={[0, 0.5, 0]}
      />

      {/* Ambient lighting */}
      <ambientLight intensity={0.4} />
      <directionalLight position={[3, 5, 2]} intensity={0.8} color="#e2e8f0" />
      <pointLight position={[-3, 3, -2]} intensity={0.4} color="#6366f1" />
      <pointLight position={[3, 3, 2]} intensity={0.3} color="#10b981" />
    </group>
  );
}

export default function LabScene3D({ constraints, protocol, className }: LabScene3DProps) {
  return (
    <div className={cn('rounded-lg border border-border bg-card overflow-hidden', className)}>
      <div className="px-3 py-2 border-b border-border flex items-center gap-1.5">
        <div className="h-2 w-2 rounded-full bg-primary animate-pulse" />
        <span className="text-[10px] font-semibold">3D Lab View</span>
        <span className="ml-auto text-[9px] text-muted-foreground">drag to rotate</span>
      </div>
      <div className="h-[200px]">
        <Suspense fallback={
          <div className="flex h-full items-center justify-center text-xs text-muted-foreground">Loading 3D scene...</div>
        }>
          <Canvas
            camera={{ position: [0, 1.5, 4], fov: 45 }}
            dpr={[1, 1.5]}
          >
            <SceneContent constraints={constraints} protocol={protocol} />
          </Canvas>
        </Suspense>
      </div>
    </div>
  );
}
