import { useState, useMemo } from 'react';
import { getAllLessons, type Flashcard } from '@/data/content';
import { localDateStr } from '@/data/leitner';
import { Button } from '@/components/ui/Button';
import { Sparkles, BookOpen } from 'lucide-react';

function useDailyWord(): Flashcard {
  return useMemo(() => {
    const all = getAllLessons();
    const cards: Flashcard[] = [];
    for (const item of all) {
      for (const card of item.lesson.flashcards) {
        cards.push(card);
      }
    }
    const today = localDateStr();
    let hash = 0;
    for (let i = 0; i < today.length; i++) {
      hash = (hash * 31 + today.charCodeAt(i)) | 0;
    }
    const idx = Math.abs(hash) % cards.length;
    return cards[idx];
  }, []);
}

export function WordOfTheDay() {
  const word = useDailyWord();
  const [revealed, setRevealed] = useState(false);

  return (
    <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-sky-50 via-primary-50 to-accent-50 border border-sky-200 shadow-sm">
      {/* Decorative shapes */}
      <div className="absolute -top-8 -right-8 w-32 h-32 rounded-full bg-sky-200/30 blur-2xl" />
      <div className="absolute -bottom-10 -left-6 w-28 h-28 rounded-full bg-accent-200/25 blur-2xl" />
      <div className="absolute top-4 right-12 w-3 h-3 rounded-full bg-primary-300/40" />
      <div className="absolute bottom-6 right-20 w-2 h-2 rounded-full bg-accent-300/50" />

      <div className="relative p-6 sm:p-8">
        {/* Header */}
        <div className="flex items-center gap-2 mb-1">
          <Sparkles size={16} className="text-primary-500" />
          <p className="text-xs uppercase tracking-widest text-primary-500 font-bold">
            Dutch Word of the Day
          </p>
        </div>
        <p className="text-sm text-slate-500 mb-6">
          Ready for a quick Dutch word?
        </p>

        {/* Card body */}
        <div className="flex items-start gap-4">
          <div className="flex-shrink-0 w-12 h-12 rounded-2xl bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center text-white shadow-sm">
            <BookOpen size={24} />
          </div>

          <div className="flex-1 min-w-0">
            <h3 className="font-display text-3xl sm:text-4xl font-extrabold text-slate-800 leading-tight mb-1">
              {word.dutch}
            </h3>

            {/* Reveal area */}
            <div
              className={`transition-all duration-500 ease-out overflow-hidden ${
                revealed ? 'max-h-48 opacity-100 mt-3' : 'max-h-0 opacity-0'
              }`}
            >
              <p className="font-display text-lg font-bold text-primary-700">
                {word.english}
              </p>
              <p className="text-sm text-slate-600 mt-1 leading-relaxed">
                {word.explanation}
              </p>
            </div>
          </div>
        </div>

        {/* Button */}
        <div className="mt-5">
          {!revealed ? (
            <Button variant="primary" size="md" onClick={() => setRevealed(true)}>
              Reveal Meaning
            </Button>
          ) : (
            <button
              onClick={() => setRevealed(false)}
              className="text-sm font-semibold text-primary-600 hover:text-primary-700 transition-colors"
            >
              Hide meaning
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
