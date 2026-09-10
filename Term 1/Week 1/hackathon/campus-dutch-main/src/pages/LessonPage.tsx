import { useRouter } from '@/context/RouterContext';
import { useProgress } from '@/context/ProgressContext';
import { NavBar } from '@/components/NavBar';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { FlashcardDeck } from '@/components/FlashcardDeck';
import { Icon } from '@/components/ui/Icon';
import { getLessonById, type Difficulty } from '@/data/content';
import { buildCardId, formatDateDisplay } from '@/data/leitner';
import { ArrowLeft, CheckCircle2, Star, RotateCw, HelpCircle, Lock, Clock } from 'lucide-react';
import { useState, useCallback } from 'react';

const difficultyLabels: Record<Difficulty, string> = {
  1: 'Beginner',
  2: 'Developing',
  3: 'Confident',
};

interface LessonPageProps {
  lessonId: string;
}

export function LessonPage({ lessonId }: LessonPageProps) {
  const router = useRouter();
  const { isLessonCompleted, isQuizUnlocked, getQuizUnlockDate, state, recordFlashcardReview, recordCardAnswer } = useProgress();
  const [mode, setMode] = useState<'flashcards' | 'quiz-entry'>('flashcards');
  const [flashcardsCompleted, setFlashcardsCompleted] = useState(false);

  const lessonData = getLessonById(lessonId);

  const handleStartQuiz = useCallback(() => {
    if (!lessonData) return;
    recordFlashcardReview(lessonId);
    setMode('quiz-entry');
  }, [lessonData, lessonId, recordFlashcardReview]);

  const handleFlashcardNext = useCallback(() => {
    if (!lessonData) return;
    recordFlashcardReview(lessonId);
    setFlashcardsCompleted(true);
  }, [lessonData, lessonId, recordFlashcardReview]);

  if (!lessonData) {
    return (
      <div className="min-h-screen bg-slate-50">
        <NavBar />
        <div className="max-w-4xl mx-auto px-6 py-16 text-center">
          <h1 className="font-display text-2xl font-bold text-slate-700">Lesson not found</h1>
          <Button variant="primary" className="mt-6" onClick={() => router.navigate({ name: 'lessons' })}>
            Back to Lessons
          </Button>
        </div>
      </div>
    );
  }

  const { lesson, topic, category } = lessonData;
  const completed = isLessonCompleted(lessonId);
  const quizUnlocked = isQuizUnlocked(lessonId);
  const quizUnlockDate = getQuizUnlockDate(lessonId);
  const result = state.quizResults[lessonId];
  const isSchool = category.id === 'school-systems';

  const reviewCards = lesson.flashcards.map((fc, i) => ({
    ...fc,
    cardId: buildCardId(lessonId, i),
  }));

  return (
    <div className="min-h-screen bg-slate-50">
      <NavBar />

      <div className="max-w-4xl mx-auto px-4 sm:px-6 py-8">
        {/* Back button */}
        <button
          onClick={() => router.navigate({ name: 'lessons' })}
          className="flex items-center gap-2 text-slate-500 hover:text-slate-700 font-semibold text-sm mb-6 transition-colors"
        >
          <ArrowLeft size={18} /> All Lessons
        </button>

        {/* Lesson header */}
        <Card className="p-6 mb-8">
          <div className="flex items-start gap-4 flex-wrap">
            <div className={`flex-shrink-0 w-14 h-14 rounded-2xl flex items-center justify-center text-white ${
              isSchool ? 'bg-gradient-to-br from-primary-400 to-primary-600' : 'bg-gradient-to-br from-accent-400 to-accent-600'
            }`}>
              <Icon name={topic.icon} size={28} />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-2 flex-wrap">
                <span className={`text-xs font-bold px-2.5 py-1 rounded-full ${
                  isSchool ? 'bg-primary-100 text-primary-700' : 'bg-accent-100 text-accent-700'
                }`}>
                  Level {lesson.difficulty}: {difficultyLabels[lesson.difficulty]}
                </span>
                {completed && (
                  <span className="text-xs font-bold px-2.5 py-1 rounded-full bg-success-100 text-success-700 flex items-center gap-1">
                    <CheckCircle2 size={12} /> First pass done
                  </span>
                )}
                {result && (
                  <span className="text-xs font-bold px-2.5 py-1 rounded-full bg-accent-100 text-accent-700 flex items-center gap-1">
                    <Star size={12} /> Best: {result.percentage}%
                  </span>
                )}
              </div>
              <h1 className="font-display text-2xl font-bold text-slate-800 mb-2">{lesson.title}</h1>
              <p className="text-slate-600">{lesson.description}</p>
            </div>
          </div>
        </Card>

        {/* Mode toggle */}
        {mode === 'flashcards' ? (
          <>
            <div className="flex items-center justify-center gap-2 mb-8">
              <div className="flex bg-white rounded-xl border border-slate-200 p-1 shadow-sm">
                <button
                  onClick={() => setMode('flashcards')}
                  className="px-4 py-2 rounded-lg font-semibold text-sm bg-primary-500 text-white flex items-center gap-2"
                >
                  <RotateCw size={16} /> Flashcards
                </button>
                <button
                  onClick={() => {
                    recordFlashcardReview(lessonId);
                    setMode('quiz-entry');
                  }}
                  className="px-4 py-2 rounded-lg font-semibold text-sm text-slate-500 hover:text-slate-700 flex items-center gap-2"
                >
                  <HelpCircle size={16} /> Quiz
                </button>
              </div>
            </div>

            <FlashcardDeck
              cards={lesson.flashcards}
              onStartQuiz={handleStartQuiz}
              onComplete={handleFlashcardNext}
              onCardAnswer={(cardId, correct) => recordCardAnswer(cardId, correct)}
              reviewCards={reviewCards}
              quizUnlocked={quizUnlocked}
              quizUnlockDate={quizUnlockDate ? formatDateDisplay(quizUnlockDate) : null}
            />

            {flashcardsCompleted && (
              <div className="max-w-2xl mx-auto mt-6">
                <Card className="p-5 bg-primary-50 border-primary-200 text-center">
                  <p className="font-semibold text-primary-800 mb-2">
                    First pass done — these cards come back for review
                  </p>
                  <p className="text-sm text-primary-600">
                    You've seen all the flashcards. They'll appear in your daily review on future days to help them stick.
                  </p>
                </Card>
              </div>
            )}
          </>
        ) : (
          <QuizEntry
            lessonId={lessonId}
            quizCount={lesson.quiz.length}
            hasResult={!!result}
            bestScore={result?.percentage}
            hasIncorrect={!!(state.incorrectQuestions[lessonId]?.length)}
            incorrectCount={state.incorrectQuestions[lessonId]?.length || 0}
            quizUnlocked={quizUnlocked}
            onSwitchToFlashcards={() => setMode('flashcards')}
          />
        )}
      </div>
    </div>
  );
}

interface QuizEntryProps {
  lessonId: string;
  quizCount: number;
  hasResult: boolean;
  bestScore?: number;
  hasIncorrect: boolean;
  incorrectCount: number;
  quizUnlocked: boolean;
  onSwitchToFlashcards: () => void;
}

function QuizEntry({ lessonId, quizCount, hasResult, bestScore, hasIncorrect, incorrectCount, quizUnlocked, onSwitchToFlashcards }: QuizEntryProps) {
  const router = useRouter();

  if (!quizUnlocked) {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="flex items-center justify-center gap-2 mb-8">
          <div className="flex bg-white rounded-xl border border-slate-200 p-1 shadow-sm">
            <button
              onClick={onSwitchToFlashcards}
              className="px-4 py-2 rounded-lg font-semibold text-sm text-slate-500 hover:text-slate-700 flex items-center gap-2"
            >
              <RotateCw size={16} /> Flashcards
            </button>
            <button
              className="px-4 py-2 rounded-lg font-semibold text-sm bg-primary-500 text-white flex items-center gap-2"
            >
              <HelpCircle size={16} /> Quiz
            </button>
          </div>
        </div>

        <Card className="p-8 text-center border-slate-300">
          <div className="w-16 h-16 rounded-2xl bg-slate-200 flex items-center justify-center text-slate-400 mx-auto mb-6">
            <Lock size={32} />
          </div>
          <h2 className="font-display text-2xl font-bold text-slate-700 mb-3">Quiz Locked</h2>
          <p className="text-slate-500 mb-2 max-w-md mx-auto">
            Come back tomorrow to test what you've learned.
          </p>
          <p className="text-sm text-slate-400 mb-8 max-w-md mx-auto">
            The quiz unlocks after you've reviewed the flashcards on a different day than when you first learned them.
            This helps your brain move the words into long-term memory.
          </p>
          <div className="flex items-center justify-center gap-2 text-sm text-slate-400">
            <Clock size={16} /> Check back after a new calendar day
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="flex items-center justify-center gap-2 mb-8">
        <div className="flex bg-white rounded-xl border border-slate-200 p-1 shadow-sm">
          <button
            onClick={onSwitchToFlashcards}
            className="px-4 py-2 rounded-lg font-semibold text-sm text-slate-500 hover:text-slate-700 flex items-center gap-2"
          >
            <RotateCw size={16} /> Flashcards
          </button>
          <button
            className="px-4 py-2 rounded-lg font-semibold text-sm bg-primary-500 text-white flex items-center gap-2"
          >
            <HelpCircle size={16} /> Quiz
          </button>
        </div>
      </div>

      <Card className="p-8 text-center">
        <div className="w-16 h-16 rounded-2xl bg-accent-100 flex items-center justify-center text-accent-600 mx-auto mb-6">
          <HelpCircle size={32} />
        </div>
        <h2 className="font-display text-2xl font-bold text-slate-800 mb-3">Ready for the Quiz?</h2>
        <p className="text-slate-600 mb-2">
          This quiz has {quizCount} multiple-choice questions about the Dutch words you just learned.
        </p>
        <p className="text-sm text-slate-500 mb-8">
          Score 80% or higher to unlock the next difficulty level.
        </p>

        {hasResult && bestScore !== undefined && (
          <div className="bg-accent-50 rounded-xl p-4 mb-6 inline-block">
            <p className="text-sm text-accent-700 font-semibold flex items-center gap-2 justify-center">
              <Star size={16} /> Your best score: {bestScore}%
            </p>
          </div>
        )}

        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <Button variant="primary" size="lg" onClick={() => router.navigate({ name: 'quiz', lessonId })}>
            Start Quiz
          </Button>
          {hasIncorrect && incorrectCount > 0 && (
            <Button variant="accent" size="lg" onClick={() => router.navigate({ name: 'quiz', lessonId, retryIncorrect: true })}>
              Retry {incorrectCount} Incorrect
            </Button>
          )}
        </div>
      </Card>
    </div>
  );
}
