import confetti from 'canvas-confetti';

export function fireSuccessConfetti() {
  // Two bursts from the sides
  const defaults = {
    spread: 60,
    ticks: 100,
    gravity: 0.8,
    decay: 0.94,
    startVelocity: 30,
    colors: ['#6366f1', '#10b981', '#3b82f6', '#f59e0b', '#34d399'],
  };

  confetti({
    ...defaults,
    particleCount: 50,
    origin: { x: 0.2, y: 0.6 },
    angle: 60,
  });
  confetti({
    ...defaults,
    particleCount: 50,
    origin: { x: 0.8, y: 0.6 },
    angle: 120,
  });

  // Center burst after a brief delay
  setTimeout(() => {
    confetti({
      particleCount: 80,
      spread: 100,
      origin: { y: 0.55 },
      colors: ['#6366f1', '#818cf8', '#10b981', '#34d399', '#f59e0b'],
      ticks: 120,
      gravity: 0.7,
    });
  }, 300);
}

export function fireGavelConfetti() {
  // Small focused burst from the judge area (center-top)
  confetti({
    particleCount: 30,
    spread: 40,
    origin: { x: 0.5, y: 0.3 },
    colors: ['#f59e0b', '#fbbf24', '#d97706'],
    ticks: 60,
    gravity: 1.2,
    startVelocity: 15,
    shapes: ['circle'],
    scalar: 0.8,
  });
}
