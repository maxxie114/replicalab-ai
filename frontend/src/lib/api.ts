import type {
  EpisodeState,
  ResetParams,
  ScientistAction,
  StepResult,
  ScenarioTemplate,
  Difficulty,
  NegotiationMessage,
  ScoreBreakdown,
  JudgeAudit,
  Protocol,
} from '@/types';

const BASE_URL = '/api';
const WS_URL = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws`;

export async function healthCheck(): Promise<{ status: string }> {
  const res = await fetch(`${BASE_URL}/health`);
  return res.json();
}

export async function getScenarios(): Promise<{ templates: ScenarioTemplate[]; difficulties: Difficulty[] }> {
  const res = await fetch(`${BASE_URL}/scenarios`);
  if (!res.ok) throw new Error('Failed to fetch scenarios');
  return res.json();
}

export async function resetEpisode(params: ResetParams): Promise<EpisodeState> {
  const res = await fetch(`${BASE_URL}/reset`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });
  if (!res.ok) throw new Error('Failed to reset episode');
  return res.json();
}

export async function stepEpisode(action: ScientistAction): Promise<StepResult> {
  const res = await fetch(`${BASE_URL}/step`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(action),
  });
  if (!res.ok) throw new Error('Failed to step episode');
  return res.json();
}

export async function getReplay(episodeId: string): Promise<EpisodeState> {
  const res = await fetch(`${BASE_URL}/replay/${episodeId}`);
  if (!res.ok) throw new Error('Failed to fetch replay');
  return res.json();
}

export type WebSocketMessage =
  | { type: 'reset'; params: ResetParams }
  | { type: 'step'; action: ScientistAction }
  | { type: 'state' };

export type WebSocketResponse =
  | { type: 'state'; data: EpisodeState }
  | { type: 'step_result'; data: StepResult }
  | { type: 'error'; message: string };

export function createWebSocket(
  onMessage: (msg: WebSocketResponse) => void,
  onOpen?: () => void,
  onClose?: () => void,
  onError?: (err: Event) => void,
): WebSocket {
  const ws = new WebSocket(WS_URL);

  ws.onopen = () => onOpen?.();
  ws.onclose = () => onClose?.();
  ws.onerror = (e) => onError?.(e);
  ws.onmessage = (event) => {
    try {
      const msg = JSON.parse(event.data) as WebSocketResponse;
      onMessage(msg);
    } catch {
      console.error('Failed to parse WebSocket message:', event.data);
    }
  };

  return ws;
}

export function sendWsMessage(ws: WebSocket, msg: WebSocketMessage) {
  if (ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify(msg));
  }
}

function createMockConversation(): NegotiationMessage[] {
  return [
    {
      role: 'scientist',
      round: 1,
      action: {
        action_type: 'propose_protocol',
        sample_size: 5,
        controls: ['random_baseline', 'published_checkpoint'],
        technique: 'fine_tuning',
        duration_days: 3,
        required_equipment: ['gpu_a100', 'wandb_logger'],
        required_reagents: ['imagenet_subset', 'pretrained_weights'],
        rationale: 'Fine-tuning a ViT-B/16 with the same hyperparameters should reproduce the top-1 accuracy within 1%. Using 5 seeds for statistical significance.',
      },
      message: 'I propose fine-tuning ViT-B/16 on the ImageNet subset with the original hyperparameters. 5 random seeds, AdamW optimizer, cosine LR schedule. Target: reproduce 82.3% top-1 accuracy within 1% margin.',
      timestamp: Date.now() - 60000,
    },
    {
      role: 'lab_manager',
      round: 1,
      action: {
        action_type: 'report_feasibility',
        feasibility_report: {
          budget_ok: false,
          equipment_ok: true,
          reagents_ok: true,
          schedule_ok: true,
          personnel_ok: true,
          issues: ['5 seeds x 3 days each = 15 GPU-days. Budget only covers 10 GPU-days on A100. Consider reducing to 3 seeds or using A6000 GPUs.'],
        },
        message: 'A100 GPUs are available but 5 seeds would exceed our 10 GPU-day budget. I suggest reducing to 3 seeds or switching to A6000 GPUs which are cheaper. Data pipeline and WandB logging are ready.',
      },
      message: 'A100 GPUs are available but 5 seeds would exceed our 10 GPU-day budget. I suggest reducing to 3 seeds or switching to A6000 GPUs which are cheaper. Data pipeline and WandB logging are ready.',
      timestamp: Date.now() - 30000,
    },
    {
      role: 'scientist',
      round: 2,
      action: {
        action_type: 'revise_protocol',
        sample_size: 3,
        controls: ['random_baseline', 'published_checkpoint'],
        technique: 'fine_tuning',
        duration_days: 3,
        required_equipment: ['gpu_a100', 'wandb_logger'],
        required_reagents: ['imagenet_subset', 'pretrained_weights'],
        rationale: 'Reduced to 3 seeds. Still enough for mean and std reporting. A100 preferred over A6000 to match original paper\'s compute setup.',
      },
      message: 'Revised to 3 seeds on A100 — fits within the 10 GPU-day budget (3 seeds x 3 days = 9 GPU-days). Keeping A100 to match the original compute environment. 3 seeds still gives us mean ± std for the accuracy claim.',
      timestamp: Date.now() - 15000,
    },
  ];
}

function createMockScores(): ScoreBreakdown {
  return {
    rigor: 0.85,
    feasibility: 0.93,
    fidelity: 0.80,
    total_reward: 8.12,
    efficiency_bonus: 0.6,
    communication_bonus: 0.4,
    penalties: 0.15,
    penalty_reasons: ['Reduced seed count from 5 to 3'],
  };
}

export function createMockEpisodeState(done = false): EpisodeState {
  const scores = done ? createMockScores() : null;
  return {
    episode_id: 'ep-mock-001',
    seed: 42,
    template: 'ml_benchmark',
    difficulty: 'medium',
    round: done ? 3 : 2,
    max_rounds: 5,
    done,
    paper: {
      title: 'An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale',
      hypothesis: 'Vision Transformers (ViT) pre-trained on large datasets match or exceed CNN performance on image classification benchmarks',
      method: 'Fine-tune ViT-B/16 on ImageNet-1k with AdamW, cosine schedule, 300 epochs, batch size 4096 across 8x A100 GPUs',
      key_finding: 'ViT-B/16 achieves 82.3% top-1 accuracy on ImageNet, outperforming ResNet-152 when pre-trained on JFT-300M',
      original_sample_size: 5,
      original_technique: 'fine_tuning',
      original_controls: ['random_baseline', 'published_checkpoint', 'resnet_comparison'],
      original_duration_days: 5,
    },
    lab_constraints: {
      budget: 2000,
      budget_remaining: 1100,
      equipment_available: ['gpu_a100', 'gpu_a6000', 'wandb_logger', 'docker_env'],
      reagents_available: ['imagenet_subset', 'pretrained_weights', 'jft_embeddings'],
      staff_count: 2,
      booking_conflicts: ['A100 cluster maintenance window Sat 2-6 AM'],
      safety_rules: ['Max 4 concurrent GPU jobs per user', 'Results must be logged to WandB'],
    },
    protocol: {
      sample_size: 3,
      controls: ['random_baseline', 'published_checkpoint'],
      technique: 'fine_tuning',
      duration_days: 3,
      required_equipment: ['gpu_a100', 'wandb_logger'],
      required_reagents: ['imagenet_subset', 'pretrained_weights'],
    },
    conversation: createMockConversation(),
    scores,
    judge_audit: done
      ? {
          verdict: 'success',
          judge_notes: [
            'Seed reduction from 5 to 3 is acceptable — still provides mean \u00b1 std',
            'Keeping A100 matches original compute environment faithfully',
            'Budget-aware revision demonstrates practical negotiation',
          ],
          top_failure_reasons: [],
          score_breakdown: scores!,
        }
      : null,
  };
}

export function createMockProtocol(): Protocol {
  return {
    sample_size: 3,
    controls: ['random_baseline', 'published_checkpoint'],
    technique: 'fine_tuning',
    duration_days: 3,
    required_equipment: ['gpu_a100', 'wandb_logger'],
    required_reagents: ['imagenet_subset', 'pretrained_weights'],
  };
}

export function createMockJudgeAudit(): JudgeAudit {
  return {
    verdict: 'success',
    judge_notes: [
      'Seed reduction from 5 to 3 is acceptable — still provides mean \u00b1 std',
      'Keeping A100 matches original compute environment faithfully',
      'Budget-aware revision demonstrates practical negotiation',
    ],
    top_failure_reasons: [],
    score_breakdown: createMockScores(),
  };
}
