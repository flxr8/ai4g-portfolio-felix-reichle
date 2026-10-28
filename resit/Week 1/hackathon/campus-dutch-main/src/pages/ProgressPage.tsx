import { useState } from 'react';
import { useRouter } from '@/context/RouterContext';
import { useProgress } from '@/context/ProgressContext';
import { NavBar } from '@/components/NavBar';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { BadgeGrid } from '@/components/BadgeGrid';
import { categories } from '@/data/content';
import { Trash2, AlertTriangle, CheckCircle2, XCircle } from 'lucide-react';

export function ProgressPage() {
  const router = useRouter();
  const { state, getOverallProgress, getCategoryProgress, resetProgress } = useProgress();
  const [showResetModal, setShowResetModal] = useState(false);

  const overall = getOverallProgress();

  const handleReset = () => {
    resetProgress();
    setShowResetModal(false);
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <NavBar />

      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8 space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div>
            <h1 className="font-display text-3xl font-bold text-slate-800 mb-2">Your Progress</h1>
            <p className="text-slate-600">Track your lessons, scores and badges. All progress is saved on this device.</p>
          </div>
        </div>

        {/* Overall progress */}
        <Card className="p-6">
          <h2 className="font-display font-bold text-lg text-slate-800 mb-4">Overall Learning Progress</h2>
          <ProgressBar value={overall.completed} max={overall.total} label="Lessons completed" showPercentage color="primary" />
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-6">
            <div className="text-center">
              <p className="font-display text-3xl font-extrabold text-primary-600">{overall.completed}</p>
              <p className="text-xs text-slate-500 mt-1">Lessons Done</p>
            </div>
            <div className="text-center">
              <p className="font-display text-3xl font-extrabold text-accent-600">{state.earnedBadges.length}</p>
              <p className="text-xs text-slate-500 mt-1">Badges Earned</p>
            </div>
            <div className="text-center">
              <p className="font-display text-3xl font-extrabold text-success-600">
                {Object.values(state.quizResults).filter((r) => r.percentage >= 80).length}
              </p>
              <p className="text-xs text-slate-500 mt-1">High Scores (80%+)</p>
            </div>
            <div className="text-center">
              <p className="font-display text-3xl font-extrabold text-secondary-600">
                {Object.values(state.quizResults).filter((r) => r.percentage === 100).length}
              </p>
              <p className="text-xs text-slate-500 mt-1">Perfect Scores</p>
            </div>
          </div>
        </Card>

        {/* Category progress */}
        <div>
          <h2 className="font-display text-xl font-bold text-slate-800 mb-4">Category Progress</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {categories.map((cat) => {
              const progress = getCategoryProgress(cat.id);
              const isSchool = cat.id === 'school-systems';
              return (
                <Card key={cat.id} className="p-5">
                  <div className="flex items-center gap-3 mb-4">
                    <div className={`w-10 h-10 rounded-xl flex items-center justify-center text-white ${
                      isSchool ? 'bg-gradient-to-br from-primary-400 to-primary-600' : 'bg-gradient-to-br from-accent-400 to-accent-600'
                    }`}>
                      {isSchool ? <CheckCircle2 size={20} /> : <XCircle size={20} />}
                    </div>
                    <h3 className="font-display font-bold text-base text-slate-800">{cat.title}</h3>
                  </div>
                  <ProgressBar
                    value={progress.completed}
                    max={progress.total}
                    label={`${progress.completed}/${progress.total} lessons`}
                    showPercentage
                    color={isSchool ? 'primary' : 'accent'}
                  />
                </Card>
              );
            })}
          </div>
        </div>

        {/* Badges */}
        <div>
          <h2 className="font-display text-xl font-bold text-slate-800 mb-4">Badges</h2>
          <BadgeGrid />
        </div>

        {/* Settings */}
        <Card className="p-6">
          <h2 className="font-display font-bold text-lg text-slate-800 mb-2">Settings</h2>
          <p className="text-sm text-slate-500 mb-4">
            Your progress is stored locally in your browser. Resetting will erase all completed lessons, quiz scores, unlocked levels and badges.
          </p>
          <Button variant="error" size="md" onClick={() => setShowResetModal(true)}>
            <Trash2 size={18} /> Reset All Progress
          </Button>
        </Card>
      </div>

      {/* Reset confirmation modal */}
      {showResetModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4" onClick={() => setShowResetModal(false)}>
          <div className="p-6 max-w-md w-full animate-pop bg-white rounded-2xl shadow-sm border border-slate-200" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 rounded-full bg-error-100 flex items-center justify-center text-error-600">
                <AlertTriangle size={24} />
              </div>
              <h2 className="font-display text-xl font-bold text-slate-800">Reset All Progress?</h2>
            </div>
            <p className="text-slate-600 mb-6">
              This will permanently erase all your completed lessons, quiz scores, unlocked levels and earned badges. This action cannot be undone.
            </p>
            <div className="flex gap-3 justify-end">
              <Button variant="ghost" size="md" onClick={() => setShowResetModal(false)}>
                Cancel
              </Button>
              <Button variant="error" size="md" onClick={handleReset}>
                <Trash2 size={18} /> Yes, Reset Everything
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
