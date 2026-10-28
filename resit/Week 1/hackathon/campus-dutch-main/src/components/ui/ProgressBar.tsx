interface ProgressBarProps {
  value: number;
  max: number;
  label?: string;
  color?: 'primary' | 'accent' | 'success' | 'secondary';
  showPercentage?: boolean;
}

const colorClasses = {
  primary: 'bg-primary-500',
  accent: 'bg-accent-500',
  success: 'bg-success-500',
  secondary: 'bg-secondary-500',
};

export function ProgressBar({ value, max, label, color = 'primary', showPercentage = false }: ProgressBarProps) {
  const percentage = max > 0 ? Math.round((value / max) * 100) : 0;

  return (
    <div className="w-full">
      {label && (
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-semibold text-slate-700">{label}</span>
          {showPercentage && (
            <span className="text-sm font-bold text-slate-600">{percentage}%</span>
          )}
        </div>
      )}
      <div
        className="w-full h-3 bg-slate-200 rounded-full overflow-hidden"
        role="progressbar"
        aria-valuenow={value}
        aria-valuemin={0}
        aria-valuemax={max}
        aria-label={label || 'Progress'}
      >
        <div
          className={`h-full ${colorClasses[color]} rounded-full transition-all duration-500 ease-out`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}
