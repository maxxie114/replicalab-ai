import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { FlaskConical, LayoutDashboard, Play, Sun, Moon, Volume2, VolumeX, HelpCircle, GitCompareArrows } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useTheme } from '@/lib/useTheme';
import { toggleMute, isMuted } from '@/lib/audio';

const navItems = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/episode', label: 'Episode', icon: Play },
  { to: '/compare', label: 'Compare', icon: GitCompareArrows },
];

export default function Header({ onShowTutorial }: { onShowTutorial?: () => void }) {
  const location = useLocation();
  const { theme, toggleTheme } = useTheme();
  const [muted, setMuted] = useState(isMuted());

  function handleToggleMute() {
    const newVal = toggleMute();
    setMuted(newVal);
  }

  return (
    <header className="sticky top-0 z-50 border-b border-border bg-background/80 backdrop-blur-sm">
      <div className="mx-auto flex h-14 max-w-screen-2xl items-center gap-6 px-4">
        <Link to="/" className="flex items-center gap-2 font-semibold text-primary">
          <FlaskConical className="h-5 w-5" />
          <span>ReplicaLab</span>
        </Link>

        <nav className="flex items-center gap-1">
          {navItems.map(({ to, label, icon: Icon }) => {
            const active = location.pathname === to || (to !== '/' && location.pathname.startsWith(to));
            return (
              <Link
                key={to}
                to={to}
                className={cn(
                  'flex items-center gap-1.5 rounded-md px-3 py-1.5 text-sm transition-colors',
                  active
                    ? 'bg-primary/10 text-primary font-medium'
                    : 'text-muted-foreground hover:text-foreground hover:bg-muted',
                )}
              >
                <Icon className="h-4 w-4" />
                {label}
              </Link>
            );
          })}
        </nav>

        <div className="ml-auto flex items-center gap-1.5">
          <span className="mr-2 text-xs text-muted-foreground hidden sm:inline">OpenEnv Hackathon</span>

          {onShowTutorial && (
            <button
              onClick={onShowTutorial}
              className="rounded-md border border-border p-1.5 text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
              title="Show tutorial"
            >
              <HelpCircle className="h-4 w-4" />
            </button>
          )}

          <button
            onClick={handleToggleMute}
            className="rounded-md border border-border p-1.5 text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
            title={muted ? 'Unmute sounds' : 'Mute sounds'}
          >
            {muted ? <VolumeX className="h-4 w-4" /> : <Volume2 className="h-4 w-4" />}
          </button>

          <button
            onClick={toggleTheme}
            className="rounded-md border border-border p-1.5 text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
            title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
          >
            {theme === 'dark' ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
          </button>
        </div>
      </div>
    </header>
  );
}
