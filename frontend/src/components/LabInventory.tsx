import { Warehouse, DollarSign, Users, AlertTriangle, Shield } from 'lucide-react';
import type { LabConstraints } from '@/types';
import { cn } from '@/lib/utils';

interface LabInventoryProps {
  constraints: LabConstraints;
  className?: string;
}

export default function LabInventory({ constraints, className }: LabInventoryProps) {
  const budgetPercent = (constraints.budget_remaining / constraints.budget) * 100;
  return (
    <div className={cn('rounded-lg border border-border bg-card p-4', className)}>
      <div className="mb-3 flex items-center gap-2">
        <Warehouse className="h-4 w-4 text-lab-manager" />
        <h2 className="text-sm font-semibold">Lab Inventory</h2>
      </div>
      <div className="space-y-3">
        <div>
          <div className="mb-1 flex items-center justify-between text-xs">
            <span className="flex items-center gap-1 font-medium"><DollarSign className="h-3 w-3" />Budget</span>
            <span className="text-muted-foreground">${constraints.budget_remaining.toLocaleString()} / ${constraints.budget.toLocaleString()}</span>
          </div>
          <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
            <div className={cn('h-full rounded-full transition-all', budgetPercent > 50 ? 'bg-lab-manager' : budgetPercent > 20 ? 'bg-judge' : 'bg-destructive')} style={{ width: `${budgetPercent}%` }} />
          </div>
        </div>
        <div><div className="mb-1 flex items-center gap-1 text-xs font-medium"><Users className="h-3 w-3" />Staff: {constraints.staff_count}</div></div>
        <div>
          <div className="mb-1 text-xs font-medium">Equipment Available</div>
          <div className="flex flex-wrap gap-1">
            {constraints.equipment_available.map((e) => <span key={e} className="rounded-full bg-lab-manager/10 px-2 py-0.5 text-xs text-lab-manager">{e.replace(/_/g, ' ')}</span>)}
          </div>
        </div>
        <div>
          <div className="mb-1 text-xs font-medium">Reagents Available</div>
          <div className="flex flex-wrap gap-1">
            {constraints.reagents_available.map((r) => <span key={r} className="rounded-full bg-scientist/10 px-2 py-0.5 text-xs text-scientist">{r.replace(/_/g, ' ')}</span>)}
          </div>
        </div>
        {constraints.booking_conflicts.length > 0 && (
          <div className="rounded-md bg-judge/5 border border-judge/20 p-2">
            <div className="mb-1 flex items-center gap-1 text-xs font-medium text-judge"><AlertTriangle className="h-3 w-3" />Booking Conflicts</div>
            <ul className="space-y-0.5 text-xs text-muted-foreground">{constraints.booking_conflicts.map((c, i) => <li key={i}>• {c}</li>)}</ul>
          </div>
        )}
        {constraints.safety_rules.length > 0 && (
          <div>
            <div className="mb-1 flex items-center gap-1 text-xs font-medium text-muted-foreground"><Shield className="h-3 w-3" />Safety</div>
            <ul className="space-y-0.5 text-xs text-muted-foreground">{constraints.safety_rules.map((r, i) => <li key={i}>• {r}</li>)}</ul>
          </div>
        )}
      </div>
    </div>
  );
}
