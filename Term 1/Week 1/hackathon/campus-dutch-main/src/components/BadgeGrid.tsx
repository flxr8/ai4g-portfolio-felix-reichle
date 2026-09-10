import { Icon } from '@/components/ui/Icon';
import { Card } from '@/components/ui/Card';
import { badges, useProgress } from '@/context/ProgressContext';

export function BadgeGrid() {
  const { state } = useProgress();
  const earnedSet = new Set(state.earnedBadges);

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {badges.map((badge) => {
        const earned = earnedSet.has(badge.id);
        return (
          <Card
            key={badge.id}
            className={`p-5 flex items-center gap-4 ${earned ? 'border-accent-300 bg-accent-50' : 'opacity-75'}`}
          >
            <div
              className={`flex-shrink-0 w-14 h-14 rounded-full flex items-center justify-center ${
                earned ? 'bg-accent-400 text-white' : 'bg-slate-200 text-slate-400'
              }`}
            >
              <Icon name={earned ? badge.icon : 'Lock'} size={28} />
            </div>
            <div className="flex-1 min-w-0">
              <h3 className={`font-display font-bold text-base ${earned ? 'text-accent-800' : 'text-slate-500'}`}>
                {badge.title}
              </h3>
              <p className={`text-sm mt-1 ${earned ? 'text-accent-700' : 'text-slate-400'}`}>
                {badge.description}
              </p>
              <p className={`text-xs mt-1 font-semibold ${earned ? 'text-success-600' : 'text-slate-400'}`}>
                {earned ? 'Earned' : 'Locked'}
              </p>
            </div>
          </Card>
        );
      })}
    </div>
  );
}
