import { useRouter } from '@/context/RouterContext';
import { useProgress } from '@/context/ProgressContext';
import { NavBar } from '@/components/NavBar';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { Icon } from '@/components/ui/Icon';
import { categories, badges } from '@/data/content';
import { WordOfTheDay } from '@/components/WordOfTheDay';
import { ArrowRight, Star, TrendingUp, Clock, CheckCircle2, BookOpen } from 'lucide-react';

export function DashboardPage() {
  const router = useRouter();
  const {
    getDueQuizCount,
    getDueQuizzes,
    getOverallProgress,
    getCategoryProgress,
    getRecommendedLesson,
    state,
  } = useProgress();

  const dueCount = getDueQuizCount();
  const dueQuizzes = getDueQuizzes();
  const overall = getOverallProgress();
  const recommended = getRecommendedLesson();
  const earnedBadges = badges.filter((b) => state.earnedBadges.includes(b.id));
  const hasStarted = overall.completed > 0 || Object.keys(state.firstLearnedDates).length > 0;

  return (
    <div className="min-h-screen bg-slate-50">
      <NavBar />

      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8 space-y-8">
        {/* Welcome message */}
        <div className="bg-gradient-to-r from-primary-600 to-primary-700 rounded-3xl p-6 sm:p-8 text-white shadow-lg">
          <h1 className="font-display text-2xl sm:text-3xl font-bold mb-2">
            Welkom bij Campus Dutch!
          </h1>
          <p className="text-primary-100 text-base sm:text-lg">
            Ready to learn the Dutch you need for university life. Let's pick up where you left off.
          </p>
        </div>

        {/* Today's Review */}
        <Card className={`p-6 sm:p-8 ${dueCount > 0 || !hasStarted ? 'border-primary-300 bg-gradient-to-r from-primary-50 to-white' : 'border-success-200 bg-gradient-to-r from-success-50 to-white'}`}>
          <div className="flex items-center justify-between gap-4 flex-wrap">
            <div className="flex items-center gap-4">
              <div className={`flex-shrink-0 w-14 h-14 rounded-2xl flex items-center justify-center text-white ${
                dueCount > 0 || !hasStarted ? 'bg-primary-500' : 'bg-success-500'
              }`}>
                {dueCount > 0 ? <Clock size={28} /> : hasStarted ? <CheckCircle2 size={28} /> : <BookOpen size={28} />}
              </div>
              <div>
                <p className="text-xs uppercase tracking-widest text-primary-500 font-bold mb-1">Today's Review</p>
                {dueCount > 0 ? (
                  <>
                    <h3 className="font-display font-bold text-xl text-slate-800">
                      {dueCount} quiz{dueCount !== 1 ? 'zes' : ''} due for review
                    </h3>
                    <p className="text-sm text-slate-500 mt-1">
                      {dueQuizzes.slice(0, 2).map(q => q.title).join(', ')}{dueQuizzes.length > 2 ? ' and more' : ''}
                    </p>
                  </>
                ) : hasStarted ? (
                  <>
                    <h3 className="font-display font-bold text-xl text-slate-800">
                      You're all caught up!
                    </h3>
                    <p className="text-sm text-slate-500 mt-1">
                      Come back tomorrow to keep building your Dutch vocabulary.
                    </p>
                  </>
                ) : (
                  <>
                    <h3 className="font-display font-bold text-xl text-slate-800">
                      Start your first lesson
                    </h3>
                    <p className="text-sm text-slate-500 mt-1">
                      Browse lessons to begin learning Dutch. Reviews will appear here after your first quiz.
                    </p>
                  </>
                )}
              </div>
            </div>
            {dueCount > 0 ? (
              <Button variant="primary" size="lg" onClick={() => router.navigate({ name: 'lessons' })}>
                Review Now <ArrowRight size={20} />
              </Button>
            ) : !hasStarted && (
              <Button variant="primary" size="lg" onClick={() => router.navigate({ name: 'lessons' })}>
                Browse Lessons <ArrowRight size={20} />
              </Button>
            )}
          </div>
        </Card>

        {/* Word of the Day */}
        <WordOfTheDay />

        {/* Stats row */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card className="p-6 md:col-span-2">
            <div className="flex items-center gap-2 mb-4">
              <TrendingUp size={20} className="text-primary-600" />
              <h2 className="font-display font-bold text-lg text-slate-800">Overall Progress</h2>
            </div>
            <ProgressBar value={overall.completed} max={overall.total} label="Lessons completed" showPercentage color="primary" />
            <p className="mt-3 text-sm text-slate-500">
              {overall.completed} of {overall.total} lessons completed
            </p>
          </Card>

          <Card className="p-6">
            <div className="flex items-center gap-2 mb-4">
              <Star size={20} className="text-accent-500" />
              <h2 className="font-display font-bold text-lg text-slate-800">Badges Earned</h2>
            </div>
            <div className="flex items-center gap-3">
              <span className="font-display text-4xl font-extrabold text-accent-600">{earnedBadges.length}</span>
              <span className="text-sm text-slate-500">of {badges.length} badges</span>
            </div>
            <div className="flex gap-1.5 mt-3">
              {badges.map((b) => (
                <div
                  key={b.id}
                  className={`w-8 h-8 rounded-full flex items-center justify-center ${
                    state.earnedBadges.includes(b.id) ? 'bg-accent-400 text-white' : 'bg-slate-200 text-slate-400'
                  }`}
                  title={b.title}
                >
                  <Icon name={state.earnedBadges.includes(b.id) ? b.icon : 'Lock'} size={16} />
                </div>
              ))}
            </div>
          </Card>
        </div>

        {/* Recommended lesson */}
        {recommended && (
          <Card className="p-6 border-primary-300 bg-gradient-to-r from-primary-50 to-white" interactive onClick={() => router.navigate({ name: 'lesson', lessonId: recommended.lessonId })}>
            <div className="flex items-center justify-between gap-4 flex-wrap">
              <div className="flex items-center gap-4">
                <div className="flex-shrink-0 w-12 h-12 rounded-2xl bg-primary-500 flex items-center justify-center text-white">
                  <Icon name="Play" size={24} />
                </div>
                <div>
                  <p className="text-xs uppercase tracking-widest text-primary-500 font-bold mb-1">Recommended next</p>
                  <h3 className="font-display font-bold text-lg text-slate-800">{recommended.title}</h3>
                </div>
              </div>
              <Button variant="primary" size="md">
                Continue Learning <ArrowRight size={18} />
              </Button>
            </div>
          </Card>
        )}

        {/* Categories */}
        <div>
          <h2 className="font-display text-xl font-bold text-slate-800 mb-4">Learning Categories</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {categories.map((cat) => {
              const progress = getCategoryProgress(cat.id);
              const isSchool = cat.id === 'school-systems';
              return (
                <Card key={cat.id} className="p-6" interactive onClick={() => router.navigate({ name: 'lessons' })}>
                  <div className="flex items-start gap-4 mb-4">
                    <div className={`flex-shrink-0 w-14 h-14 rounded-2xl flex items-center justify-center text-white ${
                      isSchool ? 'bg-gradient-to-br from-primary-400 to-primary-600' : 'bg-gradient-to-br from-accent-400 to-accent-600'
                    }`}>
                      <Icon name={cat.topics[0].icon} size={28} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-display font-bold text-lg text-slate-800">{cat.title}</h3>
                      <p className="text-sm text-slate-500 mt-1">{cat.description}</p>
                    </div>
                  </div>
                  <ProgressBar value={progress.completed} max={progress.total} label={`${progress.completed}/${progress.total} lessons`} color={isSchool ? 'primary' : 'accent'} />
                </Card>
              );
            })}
          </div>
        </div>

        {/* Continue button */}
        <div className="flex justify-center pt-2">
          <Button variant="primary" size="lg" onClick={() => router.navigate({ name: 'lessons' })}>
            Browse All Lessons <ArrowRight size={20} />
          </Button>
        </div>
      </div>
    </div>
  );
}
