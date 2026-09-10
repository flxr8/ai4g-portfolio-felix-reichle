import { useState, useEffect, useCallback } from 'react';
import { ChevronLeft, ChevronRight, RotateCw, HelpCircle, Check, X, Lock } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import type { Flashcard as FlashcardType } from '@/data/content';

export interface ReviewCard extends FlashcardType {
  cardId: string;
  box?: number;
}

interface FlashcardDeckProps {
  cards: FlashcardType[];
  onStartQuiz?: () => void;
  onComplete?: () => void;
  mode?: 'learn' | 'review';
  onCardAnswer?: (cardId: string, correct: boolean) => void;
  reviewCards?: ReviewCard[];
  quizUnlocked?: boolean;
  quizUnlockDate?: string | null;
}

export function FlashcardDeck({ cards, onStartQuiz, onComplete, mode = 'learn', onCardAnswer, reviewCards, quizUnlocked = true, quizUnlockDate }: FlashcardDeckProps) {
  const activeCards: ReviewCard[] = mode === 'review' && reviewCards
    ? reviewCards
    : cards.map((c, i) => ({ ...c, cardId: `learn-${i}` }));

  const [currentIndex, setCurrentIndex] = useState(0);
  const [flipped, setFlipped] = useState(false);
  const [direction, setDirection] = useState<'next' | 'prev'>('next');
  const [answered, setAnswered] = useState<boolean[]>(new Array(activeCards.length).fill(false));

  const card = activeCards[currentIndex];
  const isLast = currentIndex === activeCards.length - 1;

  const goNext = useCallback(() => {
    if (currentIndex < activeCards.length - 1) {
      setFlipped(false);
      setDirection('next');
      setTimeout(() => setCurrentIndex((prev) => prev + 1), 150);
    }
  }, [currentIndex, activeCards.length]);

  const goPrev = useCallback(() => {
    if (currentIndex > 0) {
      setFlipped(false);
      setDirection('prev');
      setTimeout(() => setCurrentIndex((prev) => prev - 1), 150);
    }
  }, [currentIndex]);

  const handleFlip = useCallback(() => setFlipped((f) => !f), []);

  const handleReviewAnswer = useCallback((correct: boolean) => {
    if (onCardAnswer && card.cardId) {
      onCardAnswer(card.cardId, correct);
    }
    setAnswered((prev) => {
      const next = [...prev];
      next[currentIndex] = true;
      return next;
    });
  }, [onCardAnswer, card, currentIndex]);

  const handleFinish = useCallback(() => {
    if (onComplete) {
      onComplete();
    }
  }, [onComplete]);

  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === 'ArrowRight') { e.preventDefault(); goNext(); }
      else if (e.key === 'ArrowLeft') { e.preventDefault(); goPrev(); }
      else if (e.key === ' ' || e.key === 'Enter') { e.preventDefault(); handleFlip(); }
    },
    [goNext, goPrev, handleFlip]
  );

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  const cardAnswered = answered[currentIndex];

  return (
    <div className="flex flex-col items-center w-full max-w-2xl mx-auto">
      {/* Counter */}
      <div className="mb-4 text-sm font-semibold text-slate-600" aria-live="polite">
        {currentIndex + 1} of {activeCards.length}
      </div>

      {/* Progress dots */}
      <div className="flex gap-2 mb-6 flex-wrap justify-center">
        {activeCards.map((_, i) => (
          <button
            key={i}
            onClick={() => { setFlipped(false); setDirection(i > currentIndex ? 'next' : 'prev'); setTimeout(() => setCurrentIndex(i), 150); }}
            className={`h-2.5 rounded-full transition-all duration-300 ${
              i === currentIndex ? 'w-8 bg-primary-500' : i < currentIndex ? 'w-2.5 bg-primary-300' : 'w-2.5 bg-slate-300'
            }`}
            aria-label={`Go to card ${i + 1}`}
          />
        ))}
      </div>

      {/* Flashcard */}
      <div
        key={currentIndex}
        className="card-3d-container w-full animate-fade-in"
        style={{ animation: direction === 'next' ? 'slideUp 0.4s ease-out' : 'fadeIn 0.3s ease-out' }}
      >
        <div
          className={`card-3d w-full ${flipped ? 'flipped' : ''}`}
          onClick={handleFlip}
          role="button"
          tabIndex={0}
          aria-label={`Flashcard ${currentIndex + 1}: ${flipped ? 'Showing translation' : card.dutch}. Click or press space to flip.`}
          onKeyDown={(e) => { if (e.key === ' ' || e.key === 'Enter') { e.preventDefault(); handleFlip(); } }}
          style={{ minHeight: '320px', cursor: 'pointer' }}
        >
          {/* Front */}
          <div className="card-face absolute inset-0 bg-gradient-to-br from-primary-500 to-primary-700 rounded-3xl shadow-xl flex flex-col items-center justify-center p-8 text-white">
            <div className="absolute top-4 right-4 text-white/40">
              <RotateCw size={20} />
            </div>
            {mode === 'review' && 'box' in card && (
              <p className="text-xs uppercase tracking-widest text-primary-200 font-semibold mb-4">
                Review · Box {card.box}
              </p>
            )}
            <p className="text-xs uppercase tracking-widest text-primary-200 font-semibold mb-4">Dutch</p>
            <h2 className="font-display text-3xl sm:text-4xl font-bold text-center leading-tight">
              {card.dutch}
            </h2>
            <p className="mt-6 text-sm text-primary-200 flex items-center gap-2">
              <HelpCircle size={16} /> Tap to flip
            </p>
          </div>

          {/* Back */}
          <div className="card-face card-back absolute inset-0 bg-white rounded-3xl shadow-xl flex flex-col p-6 sm:p-8 overflow-y-auto">
            <div className="absolute top-4 right-4 text-slate-300">
              <RotateCw size={20} />
            </div>
            <p className="text-xs uppercase tracking-widest text-primary-500 font-semibold mb-2">English</p>
            <h2 className="font-display text-2xl font-bold text-slate-800 mb-3">
              {card.english}
            </h2>
            <div className="space-y-3 text-sm">
              <div>
                <p className="text-xs font-bold uppercase tracking-wide text-slate-400 mb-1">Explanation</p>
                <p className="text-slate-600 leading-relaxed">{card.explanation}</p>
              </div>
              <div>
                <p className="text-xs font-bold uppercase tracking-wide text-slate-400 mb-1">University Example</p>
                <p className="text-slate-600 leading-relaxed italic">{card.example}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Controls */}
      {mode === 'review' ? (
        <div className="flex flex-col w-full mt-8 gap-4">
          {flipped ? (
            <div className="flex gap-3 justify-center">
              <Button
                variant="error"
                size="md"
                onClick={() => handleReviewAnswer(false)}
                disabled={cardAnswered}
                className="flex-1 max-w-[200px]"
              >
                <X size={20} /> Still learning
              </Button>
              <Button
                variant="success"
                size="md"
                onClick={() => handleReviewAnswer(true)}
                disabled={cardAnswered}
                className="flex-1 max-w-[200px]"
              >
                <Check size={20} /> I knew it
              </Button>
            </div>
          ) : (
            <p className="text-center text-sm text-slate-400">
              Flip the card to reveal the answer, then mark whether you knew it
            </p>
          )}
          <div className="flex items-center justify-between w-full gap-4">
            <Button
              variant="ghost"
              size="md"
              onClick={goPrev}
              disabled={currentIndex === 0}
              aria-label="Previous card"
            >
              <ChevronLeft size={20} /> Previous
            </Button>
            {isLast ? (
              <Button variant="primary" size="md" onClick={handleFinish} disabled={!cardAnswered}>
                Finish Review
              </Button>
            ) : (
              <Button
                variant="primary"
                size="md"
                onClick={goNext}
                disabled={!cardAnswered}
                aria-label="Next card"
              >
                Next <ChevronRight size={20} />
              </Button>
            )}
          </div>
        </div>
      ) : (
        <div className="flex items-center justify-between w-full mt-8 gap-4">
          <Button
            variant="ghost"
            size="md"
            onClick={goPrev}
            disabled={currentIndex === 0}
            aria-label="Previous card"
          >
            <ChevronLeft size={20} /> Previous
          </Button>
          {isLast ? (
            quizUnlocked ? (
              <Button variant="success" size="md" onClick={onStartQuiz}>
                Start Quiz
              </Button>
            ) : (
              <div className="flex flex-col items-end gap-1">
                <button
                  disabled
                  className="flex items-center gap-2 px-4 py-2 rounded-lg font-semibold text-sm bg-slate-200 text-slate-400 cursor-not-allowed"
                >
                  <Lock size={16} /> Start Quiz
                </button>
                <span className="text-xs text-slate-400">
                  {quizUnlockDate ? `Quiz unlocks on ${quizUnlockDate}` : 'Quiz available tomorrow'}
                </span>
              </div>
            )
          ) : (
            <Button variant="primary" size="md" onClick={goNext} aria-label="Next card">
              Next <ChevronRight size={20} />
            </Button>
          )}
        </div>
      )}

      {/* Keyboard hint */}
      <p className="mt-6 text-xs text-slate-400 text-center">
        Use arrow keys to navigate, space or enter to flip
      </p>
    </div>
  );
}
