import { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Float, MeshDistortMaterial, Sphere, Torus } from '@react-three/drei';
import * as THREE from 'three';

function Atom({ position, color, scale = 1 }: { position: [number, number, number]; color: string; scale?: number }) {
  const ref = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    if (!ref.current) return;
    ref.current.rotation.x = Math.sin(state.clock.elapsedTime * 0.3) * 0.2;
    ref.current.rotation.y += 0.005;
  });

  return (
    <Float speed={2} rotationIntensity={0.5} floatIntensity={1}>
      <mesh ref={ref} position={position} scale={scale}>
        <sphereGeometry args={[0.3, 32, 32]} />
        <MeshDistortMaterial color={color} speed={3} distort={0.2} roughness={0.2} metalness={0.8} />
      </mesh>
    </Float>
  );
}

function Bond({ start, end, color }: { start: [number, number, number]; end: [number, number, number]; color: string }) {
  const ref = useRef<THREE.Mesh>(null);
  const midpoint = useMemo<[number, number, number]>(() => [
    (start[0] + end[0]) / 2,
    (start[1] + end[1]) / 2,
    (start[2] + end[2]) / 2,
  ], [start, end]);

  const length = useMemo(() => {
    return Math.sqrt(
      (end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2 + (end[2] - start[2]) ** 2,
    );
  }, [start, end]);

  const rotation = useMemo(() => {
    const dir = new THREE.Vector3(end[0] - start[0], end[1] - start[1], end[2] - start[2]).normalize();
    const quat = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 1, 0), dir);
    const euler = new THREE.Euler().setFromQuaternion(quat);
    return [euler.x, euler.y, euler.z] as [number, number, number];
  }, [start, end]);

  return (
    <mesh ref={ref} position={midpoint} rotation={rotation}>
      <cylinderGeometry args={[0.04, 0.04, length, 8]} />
      <meshStandardMaterial color={color} transparent opacity={0.6} />
    </mesh>
  );
}

function Molecule({ position, rotationSpeed = 0.003 }: { position: [number, number, number]; rotationSpeed?: number }) {
  const groupRef = useRef<THREE.Group>(null);

  useFrame(() => {
    if (!groupRef.current) return;
    groupRef.current.rotation.y += rotationSpeed;
    groupRef.current.rotation.x += rotationSpeed * 0.5;
  });

  return (
    <Float speed={1.5} floatIntensity={0.8}>
      <group ref={groupRef} position={position}>
        <Atom position={[0, 0, 0]} color="#6366f1" scale={1.2} />
        <Atom position={[1, 0.5, 0]} color="#3b82f6" scale={0.8} />
        <Atom position={[-0.8, 0.8, 0.3]} color="#10b981" scale={0.8} />
        <Atom position={[0.3, -0.9, 0.5]} color="#f59e0b" scale={0.7} />
        <Atom position={[-0.5, -0.3, -0.8]} color="#3b82f6" scale={0.6} />

        <Bond start={[0, 0, 0]} end={[1, 0.5, 0]} color="#6366f1" />
        <Bond start={[0, 0, 0]} end={[-0.8, 0.8, 0.3]} color="#10b981" />
        <Bond start={[0, 0, 0]} end={[0.3, -0.9, 0.5]} color="#f59e0b" />
        <Bond start={[0, 0, 0]} end={[-0.5, -0.3, -0.8]} color="#3b82f6" />
      </group>
    </Float>
  );
}

function FloatingRing({ position, color, size = 1 }: { position: [number, number, number]; color: string; size?: number }) {
  const ref = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    if (!ref.current) return;
    ref.current.rotation.x = Math.sin(state.clock.elapsedTime * 0.5) * 0.5 + Math.PI * 0.3;
    ref.current.rotation.z += 0.008;
  });

  return (
    <Float speed={1} floatIntensity={0.5}>
      <Torus ref={ref} args={[size * 0.6, 0.05, 16, 32]} position={position}>
        <meshStandardMaterial color={color} transparent opacity={0.4} metalness={0.9} roughness={0.1} />
      </Torus>
    </Float>
  );
}

function Particles({ count = 60 }: { count?: number }) {
  const points = useMemo(() => {
    const positions = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      positions[i * 3] = (Math.random() - 0.5) * 12;
      positions[i * 3 + 1] = (Math.random() - 0.5) * 8;
      positions[i * 3 + 2] = (Math.random() - 0.5) * 6;
    }
    return positions;
  }, [count]);

  const ref = useRef<THREE.Points>(null);

  useFrame((state) => {
    if (!ref.current) return;
    ref.current.rotation.y = state.clock.elapsedTime * 0.02;
    ref.current.rotation.x = Math.sin(state.clock.elapsedTime * 0.05) * 0.1;
  });

  return (
    <points ref={ref}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" args={[points, 3]} />
      </bufferGeometry>
      <pointsMaterial size={0.03} color="#6366f1" transparent opacity={0.5} sizeAttenuation />
    </points>
  );
}

function GlowSphere({ position, color }: { position: [number, number, number]; color: string }) {
  return (
    <Float speed={2} floatIntensity={1.5}>
      <Sphere args={[0.15, 16, 16]} position={position}>
        <meshStandardMaterial color={color} emissive={color} emissiveIntensity={2} transparent opacity={0.3} />
      </Sphere>
    </Float>
  );
}

interface MoleculeSceneProps {
  className?: string;
  variant?: 'hero' | 'stage' | 'minimal';
}

export default function MoleculeScene({ className, variant = 'hero' }: MoleculeSceneProps) {
  return (
    <div className={className} style={{ pointerEvents: 'none' }}>
      <Canvas
        camera={{ position: [0, 0, 6], fov: 50 }}
        gl={{ alpha: true, antialias: true }}
        style={{ background: 'transparent' }}
      >
        <ambientLight intensity={0.4} />
        <directionalLight position={[5, 5, 5]} intensity={0.8} />
        <pointLight position={[-3, 2, 4]} intensity={0.5} color="#6366f1" />
        <pointLight position={[3, -2, 4]} intensity={0.3} color="#10b981" />

        {variant === 'hero' && (
          <>
            <Molecule position={[-3, 1.5, -1]} rotationSpeed={0.004} />
            <Molecule position={[3.5, -1, -2]} rotationSpeed={-0.003} />
            <FloatingRing position={[-2, -1.5, 0]} color="#6366f1" size={1.5} />
            <FloatingRing position={[2.5, 1, -1]} color="#10b981" size={1} />
            <FloatingRing position={[0, -0.5, -2]} color="#f59e0b" size={0.8} />
            <Particles count={80} />
            <GlowSphere position={[-4, 0, -1]} color="#3b82f6" />
            <GlowSphere position={[4, 1.5, -2]} color="#10b981" />
            <GlowSphere position={[1, -2, 0]} color="#f59e0b" />
          </>
        )}

        {variant === 'stage' && (
          <>
            <Particles count={40} />
            <FloatingRing position={[0, 0, -2]} color="#6366f1" size={2} />
            <GlowSphere position={[-3, 1, -1]} color="#3b82f6" />
            <GlowSphere position={[3, -1, -1]} color="#10b981" />
            <GlowSphere position={[0, 2, -2]} color="#f59e0b" />
          </>
        )}

        {variant === 'minimal' && (
          <>
            <Particles count={25} />
            <GlowSphere position={[-2, 0, -1]} color="#6366f1" />
            <GlowSphere position={[2, 0, -1]} color="#10b981" />
          </>
        )}
      </Canvas>
    </div>
  );
}
