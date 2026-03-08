import { useState, useEffect, useRef } from 'react';

interface TypingTextProps {
  text: string;
  speed?: number;
  onComplete?: () => void;
  className?: string;
}

export default function TypingText({ text, speed = 18, onComplete, className }: TypingTextProps) {
  const [displayed, setDisplayed] = useState('');
  const [done, setDone] = useState(false);
  const idxRef = useRef(0);
  const prevTextRef = useRef('');

  useEffect(() => {
    if (text === prevTextRef.current) return;
    prevTextRef.current = text;
    idxRef.current = 0;
    setDisplayed('');
    setDone(false);

    const interval = setInterval(() => {
      idxRef.current += 1;
      if (idxRef.current >= text.length) {
        setDisplayed(text);
        setDone(true);
        clearInterval(interval);
        onComplete?.();
      } else {
        setDisplayed(text.slice(0, idxRef.current));
      }
    }, speed);

    return () => clearInterval(interval);
  }, [text, speed, onComplete]);

  return (
    <span className={className}>
      {displayed}
      {!done && <span className="animate-pulse">|</span>}
    </span>
  );
}
