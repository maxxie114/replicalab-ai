import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatScore(value: number): string {
  return (value * 100).toFixed(0) + '%';
}

export function formatReward(value: number): string {
  return value.toFixed(2);
}

export function roleColor(role: string): string {
  switch (role) {
    case 'scientist':
      return 'text-scientist';
    case 'lab_manager':
      return 'text-lab-manager';
    case 'judge':
      return 'text-judge';
    default:
      return 'text-foreground';
  }
}

export function roleBgColor(role: string): string {
  switch (role) {
    case 'scientist':
      return 'bg-scientist/10 border-scientist/30';
    case 'lab_manager':
      return 'bg-lab-manager/10 border-lab-manager/30';
    case 'judge':
      return 'bg-judge/10 border-judge/30';
    default:
      return 'bg-muted border-border';
  }
}

export function roleLabel(role: string): string {
  switch (role) {
    case 'scientist':
      return 'Dr. Elara';
    case 'lab_manager':
      return 'Takuma';
    case 'judge':
      return 'Judge Aldric';
    default:
      return role;
  }
}

export function verdictColor(verdict: string): string {
  switch (verdict) {
    case 'success':
      return 'text-lab-manager';
    case 'partial':
      return 'text-judge';
    case 'failure':
      return 'text-destructive';
    default:
      return 'text-muted-foreground';
  }
}
