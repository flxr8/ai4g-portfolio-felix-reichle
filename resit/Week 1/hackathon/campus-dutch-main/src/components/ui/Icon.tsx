import * as Icons from 'lucide-react';
import type { LucideProps } from 'lucide-react';

interface IconProps extends LucideProps {
  name: string;
  size?: number;
  className?: string;
}

export function Icon({ name, size = 24, className = '', ...props }: IconProps) {
  const IconComponent = (Icons as unknown as Record<string, React.ComponentType<LucideProps>>)[name];
  if (!IconComponent) return null;
  return <IconComponent size={size} className={className} aria-hidden="true" {...props} />;
}
