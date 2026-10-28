import { useRouter } from '@/context/RouterContext';
import { useProgress } from '@/context/ProgressContext';
import { NavBar } from '@/components/NavBar';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { Icon } from '@/components/ui/Icon';
import { categories, type Difficulty } from '@/data/content';
import { Lock, CheckCircle2, Star, Clock } from 'lucide-react';

const difficultyLabels: Record<Difficulty, string> = {
  1: 'Beginner',
  2: 'Developing',
  3: 'Confident',
};

const difficultyColors: Record<Difficulty, string> = {
  1: 'bg-success-100 text-success-700',
  2: 'bg-accent-100 text-accent-700',
  3: 'bg-error-100 text-error-700',
};

export function LessonsOverviewPage() {
  const router = useRouter();
  const { isLessonUnlocked, isLessonCompleted, state, getCategoryProgress, getDueQuizzes } = useProgress();

  const dueQuizzes = getDueQuizzes();
  const dueLessonIds = new Set(dueQuizzes.map((q) => q.lessonId));
  const hasDue = dueLessonIds.size > 0;

  return (
    <div className="min-h-screen bg-slate-50">
      <NavBar />

      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8 space-y-8">
        <div>
          <h1 className="font-display text-3xl font-bold text-slate-800 mb-2">Lesson Overview</h1>
          <p className="text-slate-600">Choose a lesson to start learning. Complete quizzes to unlock higher difficulty levels.</p>
        </div>

        {categories.map((category) => {
          const progress = getCategoryProgress(category.id);
          const isSchool = category.id === 'school-systems';
          return (
            <div key={category.id}>
              {/* Category header */}
              <div className={`rounded-2xl p-5 mb-5 ${isSchool ? 'bg-gradient-to-r from-primary-600 to-primary-700' : 'bg-gradient-to-r from-accent-500 to-accent-600'} text-white shadow-md`}>
                <div className="flex items-center gap-3 mb-2">
                  <div className="w-10 h-10 rounded-xl bg-white/20 flex items-center justify-center">
                    <Icon name={category.topics[0].icon} size={22} />
                  </div>
                  <div>
                    <h2 className="font-display text-xl font-bold">{category.title}</h2>
                    <p className="text-sm text-white/80">{category.description}</p>
                  </div>
                </div>
                <div className="mt-3">
                  <div className="flex justify-between text-sm text-white/90 mb-1">
                    <span>{progress.completed} of {progress.total} lessons</span>
                    <span>{progress.percentage}%</span>
                  </div>
                  <div className="w-full h-2 bg-white/20 rounded-full overflow-hidden">
                    <div className="h-full bg-white rounded-full transition-all duration-500" style={{ width: `${progress.percentage}%` }} />
                  </div>
                </div>
              </div>

              {/* Topics */}
              {category.topics.map((topic) => {
                const sortedLessons = hasDue
                  ? [...topic.lessons].sort((a, b) => {
                      const aDue = dueLessonIds.has(a.id) ? 0 : 1;
                      const bDue = dueLessonIds.has(b.id) ? 0 : 1;
                      return aDue - bDue;
                    })
                  : topic.lessons;

                return (
                <div key={topic.id} className="mb-6">
                  <h3 className="font-display font-bold text-lg text-slate-700 mb-3 flex items-center gap-2">
                    <Icon name={topic.icon} size={18} className={isSchool ? 'text-primary-600' : 'text-accent-600'} />
                    {topic.title}
                  </h3>
                  <p className="text-sm text-slate-500 mb-4">{topic.description}</p>

                  {/* Lessons */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                    {sortedLessons.map((lesson) => {
                      const unlocked = isLessonUnlocked(lesson.id);
                      const completed = isLessonCompleted(lesson.id);
                      const result = state.quizResults[lesson.id];
                      const isDue = hasDue && dueLessonIds.has(lesson.id);

                      return (
                        <Card
                          key={lesson.id}
                          className={`p-5 ${!unlocked ? 'opacity-60' : ''} ${completed ? 'border-success-300' : ''} ${isDue ? 'border-primary-400 ring-2 ring-primary-200' : ''}`}
                          interactive={unlocked}
                          onClick={unlocked ? () => router.navigate({ name: 'lesson', lessonId: lesson.id }) : undefined}
                        >
                          <div className="flex items-start justify-between mb-3">
                            <span className={`text-xs font-bold px-2.5 py-1 rounded-full ${difficultyColors[lesson.difficulty]}`}>
                              Level {lesson.difficulty}: {difficultyLabels[lesson.difficulty]}
                            </span>
                            <div className="flex items-center gap-1.5">
                              {isDue && (
                                <span className="flex items-center gap-1 text-xs font-bold px-2.5 py-1 rounded-full bg-primary-100 text-primary-700">
                                  <Clock size={12} /> Review Due
                                </span>
                              )}
                              {completed && <CheckCircle2 size={20} className="text-success-500" />}
                              {!unlocked && <Lock size={20} className="text-slate-400" />}
                            </div>
                          </div>

                          <h4 className="font-display font-bold text-base text-slate-800 mb-2">{lesson.title}</h4>
                          <p className="text-sm text-slate-500 mb-3 leading-relaxed">{lesson.description}</p>

                          <div className="flex items-center gap-3 text-xs text-slate-400">
                            <span>{lesson.flashcards.length} flashcards</span>
                            <span>{lesson.quiz.length} quiz questions</span>
                          </div>

                          {result && (
                            <div className="mt-3 pt-3 border-t border-slate-100 flex items-center gap-2">
                              <Star size={14} className="text-accent-500" />
                              <span className="text-sm font-semibold text-slate-600">
                                Best score: {result.percentage}%
                              </span>
                            </div>
                          )}

                          {isDue && unlocked && (
                            <div className="mt-3 pt-3 border-t border-slate-100">
                              <Button
                                variant="primary"
                                size="sm"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  router.navigate({ name: 'quiz', lessonId: lesson.id });
                                }}
                                className="w-full"
                              >
                                <Clock size={16} /> Start Review
                              </Button>
                            </div>
                          )}

                          {!unlocked && (
                            <div className="mt-3 pt-3 border-t border-slate-100">
                              <p className="text-xs text-slate-400 flex items-center gap-1.5">
                                <Lock size={12} />
                                Score 80%+ on the previous lesson to unlock
                              </p>
                            </div>
                          )}
                        </Card>
                      );
                    })}
                  </div>
                </div>
                );
              })}
            </div>
          );
        })}
      </div>
    </div>
  );
}
