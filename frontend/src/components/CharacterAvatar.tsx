import { cn } from '@/lib/utils';

const CHARACTER_IMAGES: Record<string, string> = {
  scientist: '/characters/scientist.png',
  lab_manager: '/characters/lab-manager.png',
  judge: '/characters/judge.png',
};

const CHARACTER_NAMES: Record<string, string> = {
  scientist: 'Dr. Elara',
  lab_manager: 'Manager Takuma',
  judge: 'Judge Aldric',
};

interface CharacterAvatarProps {
  role: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  showName?: boolean;
  className?: string;
}

const sizeClasses = {
  sm: 'h-8 w-8',
  md: 'h-12 w-12',
  lg: 'h-20 w-20',
  xl: 'h-32 w-32',
};

const ringClasses: Record<string, string> = {
  scientist: 'ring-scientist/50',
  lab_manager: 'ring-lab-manager/50',
  judge: 'ring-judge/50',
};

export default function CharacterAvatar({
  role,
  size = 'md',
  showName = false,
  className,
}: CharacterAvatarProps) {
  const src = CHARACTER_IMAGES[role];
  const name = CHARACTER_NAMES[role];

  return (
    <div className={cn('flex flex-col items-center gap-1', className)}>
      <div
        className={cn(
          'overflow-hidden rounded-full ring-2 bg-muted',
          sizeClasses[size],
          ringClasses[role],
        )}
      >
        {src ? (
          <img
            src={src}
            alt={name ?? role}
            className="h-full w-full object-cover object-top"
          />
        ) : (
          <div className="flex h-full w-full items-center justify-center text-xs font-bold text-muted-foreground">
            {role.charAt(0).toUpperCase()}
          </div>
        )}
      </div>
      {showName && name && (
        <span className="text-xs font-medium text-muted-foreground">{name}</span>
      )}
    </div>
  );
}

export { CHARACTER_IMAGES, CHARACTER_NAMES };
