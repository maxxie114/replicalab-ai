let ctx: AudioContext | null = null;

function getCtx(): AudioContext {
  if (!ctx) ctx = new AudioContext();
  if (ctx.state === 'suspended') ctx.resume();
  return ctx;
}

function playTone(
  freq: number,
  duration: number,
  type: OscillatorType = 'sine',
  volume = 0.15,
  rampDown = true,
) {
  const ac = getCtx();
  const osc = ac.createOscillator();
  const gain = ac.createGain();
  osc.type = type;
  osc.frequency.value = freq;
  gain.gain.value = volume;
  if (rampDown) gain.gain.exponentialRampToValueAtTime(0.001, ac.currentTime + duration);
  osc.connect(gain).connect(ac.destination);
  osc.start();
  osc.stop(ac.currentTime + duration);
}

function playNoise(duration: number, volume = 0.04) {
  const ac = getCtx();
  const bufferSize = ac.sampleRate * duration;
  const buffer = ac.createBuffer(1, bufferSize, ac.sampleRate);
  const data = buffer.getChannelData(0);
  for (let i = 0; i < bufferSize; i++) data[i] = (Math.random() * 2 - 1) * 0.5;
  const src = ac.createBufferSource();
  src.buffer = buffer;
  const gain = ac.createGain();
  gain.gain.value = volume;
  gain.gain.exponentialRampToValueAtTime(0.001, ac.currentTime + duration);
  const filter = ac.createBiquadFilter();
  filter.type = 'highpass';
  filter.frequency.value = 4000;
  src.connect(filter).connect(gain).connect(ac.destination);
  src.start();
}

export const sfx = {
  episodeStart() {
    playTone(523, 0.15, 'sine', 0.12);
    setTimeout(() => playTone(659, 0.15, 'sine', 0.12), 100);
    setTimeout(() => playTone(784, 0.25, 'sine', 0.10), 200);
  },

  scientistSpeak() {
    playTone(440, 0.08, 'triangle', 0.06);
    setTimeout(() => playTone(520, 0.08, 'triangle', 0.05), 60);
    setTimeout(() => playTone(480, 0.12, 'triangle', 0.04), 120);
  },

  labManagerSpeak() {
    playTone(330, 0.08, 'square', 0.04);
    setTimeout(() => playTone(350, 0.10, 'square', 0.04), 70);
    setTimeout(() => playTone(310, 0.12, 'square', 0.03), 140);
  },

  judgeAppear() {
    playTone(220, 0.3, 'sawtooth', 0.06);
    playTone(330, 0.3, 'sawtooth', 0.05);
    setTimeout(() => {
      playTone(440, 0.4, 'sine', 0.10);
      playTone(554, 0.4, 'sine', 0.07);
    }, 200);
  },

  gavel() {
    playNoise(0.08, 0.12);
    playTone(180, 0.15, 'square', 0.10);
    setTimeout(() => {
      playNoise(0.06, 0.08);
      playTone(160, 0.2, 'square', 0.08);
    }, 250);
  },

  scoreReveal() {
    const notes = [523, 587, 659, 784];
    notes.forEach((f, i) => {
      setTimeout(() => playTone(f, 0.18, 'sine', 0.08), i * 90);
    });
  },

  success() {
    playTone(523, 0.12, 'sine', 0.10);
    setTimeout(() => playTone(659, 0.12, 'sine', 0.10), 120);
    setTimeout(() => playTone(784, 0.12, 'sine', 0.10), 240);
    setTimeout(() => playTone(1047, 0.3, 'sine', 0.12), 360);
  },

  failure() {
    playTone(400, 0.2, 'sawtooth', 0.07);
    setTimeout(() => playTone(350, 0.2, 'sawtooth', 0.07), 200);
    setTimeout(() => playTone(300, 0.4, 'sawtooth', 0.06), 400);
  },

  click() {
    playTone(800, 0.04, 'square', 0.05);
  },

  roundTick() {
    playTone(1200, 0.05, 'sine', 0.06);
  },

  negotiate() {
    playTone(392, 0.1, 'triangle', 0.05);
    setTimeout(() => playTone(440, 0.1, 'triangle', 0.05), 80);
  },
};
