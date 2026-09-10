import { useRouter } from '@/context/RouterContext';
import { useProgress } from '@/context/ProgressContext';
import { NavBar } from '@/components/NavBar';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Icon } from '@/components/ui/Icon';
import { getLessonById, getAllLessons, badges } from '@/data/content';
import { CheckCircle2, XCircle, ArrowRight, RotateCw, LayoutGrid, Trophy } from 'lucide-react';
import { useState, useEffect } from 'react';

interface QuizResultsPageProps {
  lessonId: string;
  score: number;
  total: number;
  incorrectIndices: string;
  retryIncorrect?: boolean;
}

export function QuizResultsPage({ lessonId, score, total, incorrectIndices, retryIncorrect }: QuizResultsPageProps) {
  const router = useRouter();
  const { state, newlyEarnedBadges, clearNewBadges } = useProgress();
  const lessonData = getLessonById(lessonId);
  const [showBadgePopup, setShowBadgePopup] = useState(false);

  const percentage = total > 0 ? Math.round((score / total) * 100) : 0;
  const incorrectIdxs = incorrectIndices
    .split(',')
    .filter(Boolean)
    .map(Number);

  useEffect(() => {
    if (newlyEarnedBadges.length > 0) {
      setShowBadgePopup(true);
    }
  }, [newlyEarnedBadges]);

  if (!lessonData) {
    return (
      <div className="min-h-screen bg-slate-50">
        <NavBar />
        <div className="max-w-4xl mx-auto px-6 py-16 text-center">
          <h1 className="font-display text-2xl font-bold text-slate-700">Results not found</h1>
          <Button variant="primary" className="mt-6" onClick={() => router.navigate({ name: 'lessons' })}>
            Back to Lessons
          </Button>
        </div>
      </div>
    );
  }

  const { lesson } = lessonData;
  const quizQuestions = lesson.quiz;

  // Determine recommendation
  let recommendation: { title: string; description: string; action?: () => void; actionLabel?: string };
  const allLessons = getAllLessons();
  const currentIdx = allLessons.findIndex((l) => l.lesson.id === lessonId);
  const nextLesson = currentIdx + 1 < allLessons.length ? allLessons[currentIdx + 1] : null;
  const nextUnlocked = nextLesson && state.unlockedLessons.includes(nextLesson.lesson.id);

  if (percentage < 60) {
    recommendation = {
      title: 'Let\'s practise a bit more',
      description: 'You scored below 60%. Try this lesson again to strengthen your understanding before moving on.',
      action: () => router.navigate({ name: 'lesson', lessonId }),
      actionLabel: 'Retry Lesson',
    };
  } else if (percentage < 80) {
    // Find another lesson at the same difficulty level
    const sameLevelLessons = allLessons.filter(
      (l) => l.lesson.difficulty === lesson.difficulty && l.lesson.id !== lessonId
    );
    const nextSameLevel = sameLevelLessons.find((l) => state.unlockedLessons.includes(l.lesson.id) && !state.completedLessons.includes(l.lesson.id));
    recommendation = {
      title: 'Good job! You passed',
      description: 'You passed this quiz. Practise another lesson at the same level to build more confidence before moving to the next difficulty.',
      action: nextSameLevel ? () => router.navigate({ name: 'lesson', lessonId: nextSameLevel.lesson.id }) : undefined,
      actionLabel: nextSameLevel ? `Try: ${nextSameLevel.lesson.title}` : 'Browse Lessons',
    };
  } else {
    recommendation = {
      title: 'Excellent! Next level unlocked',
      description: nextUnlocked
        ? `You scored 80% or higher. The next lesson is now unlocked.`
        : 'You scored 80% or higher. Great work!',
      action: nextUnlocked ? () => router.navigate({ name: 'lesson', lessonId: nextLesson!.lesson.id }) : undefined,
      actionLabel: nextUnlocked ? `Continue: ${nextLesson!.lesson.title}` : 'Browse Lessons',
    };
  }

  const passed = percentage >= 60;
  const isPerfect = percentage === 100;

  return (
    <div className="min-h-screen bg-slate-50">
      <NavBar />

      <div className="max-w-3xl mx-auto px-4 sm:px-6 py-8 space-y-6">
        {/* Score card */}
        <Card className={`p-8 text-center ${isPerfect ? 'border-accent-300 bg-gradient-to-b from-accent-50 to-white' : ''}`}>
          <div className={`w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-4 ${
            isPerfect ? 'bg-accent-400 text-white' : passed ? 'bg-success-400 text-white' : 'bg-error-400 text-white'
          }`}>
            {isPerfect ? <Trophy size={40} /> : passed ? <CheckCircle2 size={40} /> : <XCircle size={40} />}
          </div>
          <h1 className="font-display text-3xl font-bold text-slate-800 mb-2">
            {isPerfect ? 'Perfect Score!' : passed ? 'First Pass Done!' : 'Keep Practising!'}
          </h1>
          <p className="text-slate-600 mb-2">{lesson.title}</p>
          {passed && !isPerfect && (
            <p className="text-sm text-slate-500 mb-4">
              This lesson\'s cards come back for review on future days to help them stick.
            </p>
          )}

          <div className="flex items-center justify-center gap-2 mb-2">
            <span className="font-display text-5xl font-extrabold text-slate-800">{score}</span>
            <span className="font-display text-3xl font-bold text-slate-400">/ {total}</span>
          </div>
          <p className={`font-display text-2xl font-bold ${isPerfect ? 'text-accent-600' : passed ? 'text-success-600' : 'text-error-600'}`}>
            {percentage}%
          </p>
        </Card>

        {/* Recommendation */}
        <Card className="p-6 border-primary-200 bg-primary-50">
          <h2 className="font-display font-bold text-lg text-slate-800 mb-2">{recommendation.title}</h2>
          <p className="text-slate-600 text-sm mb-4">{recommendation.description}</p>
          {recommendation.action && (
            <Button variant="primary" size="md" onClick={recommendation.action}>
              {recommendation.actionLabel} <ArrowRight size={18} />
            </Button>
          )}
        </Card>

        {/* Action buttons */}
        <div className="flex flex-col sm:flex-row gap-3">
          {incorrectIdxs.length > 0 && (
            <Button
              variant="accent"
              size="md"
              className="flex-1"
              onClick={() => router.navigate({ name: 'quiz', lessonId, retryIncorrect: true })}
            >
              <RotateCw size={18} /> Retry {incorrectIdxs.length} Incorrect
            </Button>
          )}
          <Button
            variant="primary"
            size="md"
            className="flex-1"
            onClick={() => router.navigate({ name: 'quiz', lessonId })}
          >
            <RotateCw size={18} /> Retry Full Quiz
          </Button>
          <Button
            variant="outline"
            size="md"
            className="flex-1"
            onClick={() => router.navigate({ name: 'lessons' })}
          >
            <LayoutGrid size={18} /> Lesson Overview
          </Button>
        </div>

        {/* Answer review */}
        <div>
          <h2 className="font-display text-xl font-bold text-slate-800 mb-4">Answer Review</h2>
          <div className="space-y-4">
            {quizQuestions.map((q, i) => {
              const isIncorrect = incorrectIdxs.includes(i);
              const userAnswer = state.quizResults[lessonId]?.incorrectQuestionIndices.includes(i)
                ? undefined
                : undefined;

              return (
                <Card key={i} className={`p-5 ${isIncorrect ? 'border-error-200' : 'border-success-200'}`}>
                  <div className="flex items-start gap-3 mb-3">
                    {isIncorrect ? (
                      <XCircle size={22} className="text-error-500 flex-shrink-0 mt-0.5" />
                    ) : (
                      <CheckCircle2 size={22} className="text-success-500 flex-shrink-0 mt-0.5" />
                    )}
                    <div className="flex-1">
                      <p className="font-semibold text-slate-800 mb-3">{q.question}</p>
                      <div className="space-y-2">
                        {q.options.map((opt, j) => {
                          const isCorrect = j === q.correctIndex;
                          return (
                            <div
                              key={j}
                              className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm ${
                                isCorrect
                                  ? 'bg-success-50 text-success-800 font-semibold'
                                  : 'text-slate-600'
                              }`}
                            >
                              <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0 ${
                                isCorrect ? 'bg-success-500 text-white' : 'bg-slate-200 text-slate-500'
                              }`}>
                                {String.fromCharCode(65 + j)}
                              </span>
                              {opt}
                              {isCorrect && <CheckCircle2 size={16} className="text-success-500 ml-auto" />}
                            </div>
                          );
                        })}
                      </div>
                      <div className="mt-3 p-3 bg-primary-50 rounded-lg">
                        <p className="text-sm text-slate-600">
                          <span className="font-bold text-primary-700">Explanation: </span>
                          {q.explanation}
                        </p>
                      </div>
                    </div>
                  </div>
                </Card>
              );
            })}
          </div>
        </div>
      </div>

      {/* Badge popup */}
      {showBadgePopup && newlyEarnedBadges.length > 0 && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4" onClick={() => { setShowBadgePopup(false); clearNewBadges(); }}>
          <div className="p-8 max-w-md text-center animate-pop bg-white rounded-2xl shadow-sm border border-slate-200" onClick={(e) => e.stopPropagation()}>
            <div className="w-20 h-20 rounded-full bg-accent-400 flex items-center justify-center text-white mx-auto mb-4">
              <Trophy size={40} />
            </div>
            <h2 className="font-display text-2xl font-bold text-slate-800 mb-2">
              {newlyEarnedBadges.length > 1 ? 'Badges Earned!' : 'Badge Earned!'}
            </h2>
            <p className="font-display font-bold text-accent-700 mb-2">
              {newlyEarnedBadges.length} new badge{newlyEarnedBadges.length > 1 ? 's' : ''}!
            </p>
            <div className="space-y-1 mb-2">
              {newlyEarnedBadges.map((badgeId) => {
                const badge = badges.find((b) => b.id === badgeId);
                return (
                  <p key={badgeId} className="text-sm text-accent-700 font-semibold">
                    {badge?.title}
                  </p>
                );
              })}
            </div>
            <p className="text-slate-600 text-sm mb-6">
              Check the Progress page to see all your badges.
            </p>
            <Button variant="primary" size="md" onClick={() => { setShowBadgePopup(false); clearNewBadges(); }}>
              Continue
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
