# Frontend Map — `frontend/`

> React 19 + TypeScript + Vite UI for ReplicaLab.
>
> **Tasks implemented:** FND 01-10

## Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| React | 19.2.0 | UI framework |
| React Router | 7.13.1 | Client-side routing |
| Three.js | 0.183.2 | 3D molecule scene |
| @react-three/fiber | 9.5.0 | React Three.js bindings |
| @react-three/drei | 10.7.7 | Three.js helpers |
| Framer Motion | 12.35.1 | Animations |
| @xyflow/react | 12.10.1 | Flow diagrams |
| Recharts | 3.8.0 | Charts and graphs |
| Tailwind CSS | 4.2.1 | Utility-first styling |
| Lucide React | 0.577.0 | Icons |

## Routes — `App.tsx`

| Path | Component | Purpose |
|------|-----------|---------|
| `/` | `DashboardPage` | Training overview, scenario selection |
| `/episode` | `EpisodePage` | Live episode viewer (new episode) |
| `/episode/:episodeId` | `EpisodePage` | Replay of completed episode |

## Pages

### `DashboardPage.tsx`
- Scenario selection (family + difficulty)
- Training metrics display
- Episode history list
- Start new episode button

### `EpisodePage.tsx`
- Live negotiation between Scientist and Lab Manager
- Protocol display and evolution
- Score breakdown when episode completes
- Replay controls for completed episodes

## Components (15 files)

### Negotiation & Protocol
| Component | Purpose |
|-----------|---------|
| `NegotiationLog.tsx` | Scrollable conversation between agents |
| `ProtocolPanel.tsx` | Current protocol details display |
| `PaperPanel.tsx` | Paper summary (title, hypothesis, method, finding) |
| `LabInventory.tsx` | Equipment and reagent availability |
| `Controls.tsx` | User controls (start, step, auto-play) |

### Visualization
| Component | Purpose |
|-----------|---------|
| `ScorePanel.tsx` | Rigor/feasibility/fidelity score bars |
| `JudgeAuditPanel.tsx` | Judge reasoning and audit trail |
| `TrainingResults.tsx` | Training metrics charts |
| `ReplayViewer.tsx` | Step-through replay of completed episodes |

### 3D & Animation
| Component | Purpose |
|-----------|---------|
| `CharacterStage.tsx` | 3D stage for agent characters |
| `CharacterAvatar.tsx` | Individual agent avatar |
| `AnimatedCharacter.tsx` | Character with animations |
| `MoleculeScene.tsx` | 3D molecule visualization |
| `TiltCard.tsx` | Tilt-on-hover card component |

### Layout
| Component | Purpose |
|-----------|---------|
| `Header.tsx` | Top navigation bar |

## API Client — `lib/api.ts`

### REST Functions
| Function | Method | Endpoint |
|----------|--------|----------|
| `healthCheck()` | GET | `/health` |
| `getScenarios()` | GET | `/scenarios` |
| `resetEpisode(params)` | POST | `/reset` |
| `stepEpisode(action)` | POST | `/step` |
| `getReplay(episodeId)` | GET | `/replay/{episodeId}` |

### WebSocket
| Function | Purpose |
|----------|---------|
| `createWebSocket(onMessage, onOpen, onClose, onError)` | Connect to `/ws` |
| `sendWsMessage(ws, msg)` | Send typed message |

### Mock Data (for offline development)
| Function | Returns |
|----------|---------|
| `createMockConversation()` | `NegotiationMessage[]` |
| `createMockScores()` | `ScoreBreakdown` |
| `createMockEpisodeState(done)` | `EpisodeState` |
| `createMockProtocol()` | `Protocol` |
| `createMockJudgeAudit()` | `JudgeAudit` |

## TypeScript Types — `types/index.ts`

Mirrors Python models:

| TS Interface | Python Model |
|-------------|--------------|
| `ScientistAction` | `ScientistAction` |
| `LabManagerAction` | `LabManagerAction` |
| `Protocol` | `Protocol` |
| `EpisodeState` | `EpisodeState` |
| `StepResult` | `StepResult` |
| `ScoreBreakdown` | `RewardBreakdown` |
| `FeasibilityReport` | `FeasibilityCheckResult` (partial) |
| `JudgeAudit` | `StepInfo.judge_notes` + `verdict` |
| `NegotiationMessage` | `ConversationEntry` |

Additional frontend-only types:
- `TrainingMetrics` — loss, reward curves
- `TrainingComparison` — baseline vs trained model
- `PaperSummary` — paper details for display
- `LabConstraints` — lab resource summary
- `SuggestedChange` — protocol revision display

## Utility Files

### `lib/utils.ts`
Shared helpers (class merging, formatting, etc.)

### `lib/audio.ts`
Audio feedback utilities for UI interactions.

## Assets

```
frontend/public/characters/
    judge.png           (~1.2 MB)
    lab-manager.png     (~900 KB)
    scientist.png       (~900 KB)
```
