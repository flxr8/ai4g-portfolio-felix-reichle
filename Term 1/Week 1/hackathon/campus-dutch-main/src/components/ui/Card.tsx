import type { ReactNode } from 'react';

interface CardProps {
  children: ReactNode;
  className?: string;
  onClick?: () => void;
  interactive?: boolean;
}

export function Card({ children, className = '', onClick, interactive = false }: CardProps) {
  return (
    <div
      onClick={onClick}
      tabIndex={interactive ? 0 : undefined}
      role={interactive ? 'button' : undefined}
      onKeyDown={interactive ? (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onClick?.(); } } : undefined}
      className={`bg-white rounded-2xl shadow-sm border border-slate-200 ${interactive ? 'cursor-pointer hover:shadow-md hover:border-primary-300 transition-all duration-200' : ''} ${className}`}
    >
      {children}
    </div>
  );
}
