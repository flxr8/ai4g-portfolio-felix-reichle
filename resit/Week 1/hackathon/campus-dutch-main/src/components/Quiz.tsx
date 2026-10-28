import { useState, useEffect, useCallback } from 'react';
import { ChevronRight } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { ProgressBar } from '@/components/ui/ProgressBar';
import type { QuizQuestion } from '@/data/content';
import { useRouter } from '@/context/RouterContext';
import { useProgress, type QuizResult } from '@/context/ProgressContext';
import { getLessonById } from '@/data/content';

interface QuizProps {
  lessonId: string;
  questions: QuizQuestion[];
  retryIncorrect?: boolean;
  incorrectIndices?: number[];
}

export function Quiz({ lessonId, questions, retryIncorrect = false, incorrectIndices = [] }: QuizProps) {
  const router = useRouter();
  const { recordQuizResult } = useProgress();

  const activeQuestions = retryIncorrect && incorrectIndices.length > 0
    ? incorrectIndices.map((i) => ({ ...questions[i], originalIndex: i }))
    : questions.map((q, i) => ({ ...q, originalIndex: i }));

  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedOption, setSelectedOption] = useState<number | null>(null);
  const [answers, setAnswers] = useState<(number | null)[]>(new Array(activeQuestions.length).fill(null));

  const question = activeQuestions[currentIndex];
  const isLast = currentIndex === activeQuestions.length - 1;

  const handleSubmit = useCallback(() => {
    if (selectedOption === null) return;

    const newAnswers = [...answers];
    newAnswers[currentIndex] = selectedOption;
    setAnswers(newAnswers);

    if (isLast) {
      const incorrect: number[] = [];
      activeQuestions.forEach((q, i) => {
        if (newAnswers[i] !== q.correctIndex) {
          incorrect.push(q.originalIndex);
        }
      });

      const correctCount = activeQuestions.length - incorrect.length;
      const total = activeQuestions.length;
      const percentage = Math.round((correctCount / total) * 100);

      const result: QuizResult = {
        lessonId,
        score: correctCount,
        total,
        percentage,
        incorrectQuestionIndices: incorrect,
        date: new Date().toISOString(),
      };

      recordQuizResult(result);

      router.navigate({
        name: 'quiz-results',
        lessonId,
        score: correctCount,
        total,
        incorrectIndices: incorrect.join(','),
        retryIncorrect,
      });
    } else {
      setCurrentIndex((prev) => prev + 1);
      setSelectedOption(newAnswers[currentIndex + 1] ?? null);
    }
  }, [selectedOption, answers, currentIndex, isLast, activeQuestions, lessonId, recordQuizResult, router, retryIncorrect]);

  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === 'Enter' && selectedOption !== null) {
        e.preventDefault();
        handleSubmit();
      }
    },
    [handleSubmit, selectedOption]
  );

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  const lessonData = getLessonById(lessonId);

  return (
    <div className="w-full max-w-2xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-3">
          <h2 className="font-display text-xl font-bold text-slate-800">
            {retryIncorrect ? 'Retry Incorrect Questions' : 'Quiz'}
          </h2>
          <span className="text-sm font-semibold text-slate-500">
            Question {currentIndex + 1} of {activeQuestions.length}
          </span>
        </div>
        <ProgressBar
          value={currentIndex + 1}
          max={activeQuestions.length}
          color="accent"
        />
      </div>

      {/* Question */}
      <div key={currentIndex} className="animate-slide-up">
        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 sm:p-8">
          <p className="text-xs uppercase tracking-widest text-accent-500 font-semibold mb-3">
            {lessonData?.lesson.title}
          </p>
          <h3 className="font-display text-xl sm:text-2xl font-bold text-slate-800 mb-6 leading-snug">
            {question.question}
          </h3>

          {/* Options */}
          <div className="space-y-3">
            {question.options.map((option, i) => {
              const isSelected = selectedOption === i;
              return (
                <button
                  key={i}
                  onClick={() => setSelectedOption(i)}
                  className={`w-full text-left p-4 rounded-xl border-2 transition-all duration-200 flex items-center gap-3 ${
                    isSelected
                      ? 'border-primary-500 bg-primary-50 text-primary-900'
                      : 'border-slate-200 bg-white text-slate-700 hover:border-primary-300 hover:bg-primary-50/50'
                  }`}
                  aria-pressed={isSelected}
                  aria-label={`Answer option ${i + 1}: ${option}`}
                >
                  <span
                    className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm transition-all ${
                      isSelected ? 'bg-primary-500 text-white' : 'bg-slate-100 text-slate-500'
                    }`}
                  >
                    {String.fromCharCode(65 + i)}
                  </span>
                  <span className="font-medium">{option}</span>
                </button>
              );
            })}
          </div>

        </div>

        {/* Submit button */}
        <div className="flex justify-end mt-6">
          <Button
            variant={isLast ? 'success' : 'primary'}
            size="md"
            onClick={handleSubmit}
            disabled={selectedOption === null}
          >
            {isLast ? 'Finish Quiz' : 'Next Question'}
            <ChevronRight size={20} />
          </Button>
        </div>
      </div>
    </div>
  );
}
