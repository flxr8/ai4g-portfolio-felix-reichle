import { getAllLessons } from '@/data/content';
import {
  type CardStateMap,
  type CardState,
  buildCardId,
  daysFromToday,
  BOX_INTERVALS,
} from '@/data/leitner';

interface QuizResultLike {
  lessonId: string;
  score: number;
  total: number;
  percentage: number;
  incorrectQuestionIndices: number[];
  date: string;
}

interface ProgressStateLike {
  completedLessons: string[];
  unlockedLessons: string[];
  quizResults: Record<string, QuizResultLike>;
  earnedBadges: string[];
  lastLessonId: string | null;
  incorrectQuestions: Record<string, number[]>;
  cardStates: CardStateMap;
  firstLearnedDates: Record<string, string>;
  reviewSessionDates: Record<string, string[]>;
  quizCompletedDates: Record<string, string>;
}

function dayOffset(offset: number): string {
  return daysFromToday(offset);
}

function cardState(box: number, streak: number, seen: number, nextReviewOffset: number): CardState {
  return {
    box,
    correctStreak: streak,
    timesSeen: seen,
    nextReviewDate: dayOffset(nextReviewOffset),
  };
}

const INITIAL_UNLOCKED = ['grades-l1', 'deadlines-l1', 'platforms-l1', 'classroom-l1', 'talking-l1', 'asking-l1'];

export function buildDemoState(): ProgressStateLike {
  const all = getAllLessons();
  const difficulty1 = all.filter((item) => item.lesson.difficulty === 1);
  const difficulty2 = all.filter((item) => item.lesson.difficulty === 2);

  const completedLessons: string[] = [];
  const firstLearnedDates: Record<string, string> = {};
  const reviewSessionDates: Record<string, string[]> = {};
  const quizCompletedDates: Record<string, string> = {};
  const quizResults: Record<string, QuizResultLike> = {};
  const incorrectQuestions: Record<string, number[]> = {};
  const cardStates: CardStateMap = {};
  const unlockedLessons = [...INITIAL_UNLOCKED];

  // --- Difficulty 1 lessons: learned 7 days ago, quiz completed 3 days ago ---
  for (const item of difficulty1) {
    const lessonId = item.lesson.id;
    completedLessons.push(lessonId);
    firstLearnedDates[lessonId] = dayOffset(-7);
    reviewSessionDates[lessonId] = [dayOffset(-7), dayOffset(-6), dayOffset(-4), dayOffset(-1)];
    quizCompletedDates[lessonId] = dayOffset(-3);

    const total = item.lesson.quiz.length;
    // Most difficulty-1 quizzes were perfect or near-perfect
    const incorrectCount = lessonId === 'classroom-l1' ? 1 : 0;
    const score = total - incorrectCount;
    const percentage = Math.round((score / total) * 100);
    const incorrectIndices: number[] = [];
    for (let qi = 0; qi < incorrectCount; qi++) {
      incorrectIndices.push(total - 1 - qi);
    }

    quizResults[lessonId] = {
      lessonId,
      score,
      total,
      percentage,
      incorrectQuestionIndices: incorrectIndices,
      date: dayOffset(-3),
    };

    if (incorrectIndices.length > 0) {
      incorrectQuestions[lessonId] = incorrectIndices;
    }

    // Quiz card states: answered correctly multiple times over the week
    item.lesson.quiz.forEach((_q, qi) => {
      const cardId = buildCardId(lessonId, qi);
      const wasCorrect = !incorrectIndices.includes(qi);
      if (wasCorrect) {
        // Correct 3 times: box 1->2->3->4, next review in 14 days
        cardStates[cardId] = cardState(4, 3, 4, 14);
      } else {
        // Wrong initially, correct on retry 2 days ago: box 2, due tomorrow
        cardStates[cardId] = cardState(2, 1, 3, 1);
      }
    });

    // Flashcard card states: reviewed over the week, varying boxes
    item.lesson.flashcards.forEach((_fc, fi) => {
      const cardId = buildCardId(lessonId, fi);
      const box = fi % 3 === 0 ? 4 : fi % 3 === 1 ? 3 : 2;
      const interval = BOX_INTERVALS[box - 1];
      // Some cards are due today (offset negative), some in the future
      const nextReviewOffset = fi % 2 === 0 ? -(interval - 5) : interval;
      cardStates[cardId] = cardState(box, box - 1, box, nextReviewOffset);
    });
  }

  // Unlock all difficulty-2 lessons (scored >= 60% on difficulty-1 quizzes)
  for (const item of difficulty2) {
    if (!unlockedLessons.includes(item.lesson.id)) {
      unlockedLessons.push(item.lesson.id);
    }
  }

  // --- First two difficulty-2 lessons: learned 4 days ago, quiz completed 2 days ago ---
  for (let i = 0; i < Math.min(2, difficulty2.length); i++) {
    const item = difficulty2[i];
    const lessonId = item.lesson.id;
    completedLessons.push(lessonId);
    firstLearnedDates[lessonId] = dayOffset(-4);
    reviewSessionDates[lessonId] = [dayOffset(-4), dayOffset(-2), dayOffset(-1)];
    quizCompletedDates[lessonId] = dayOffset(-2);

    const total = item.lesson.quiz.length;
    const score = total - 1; // missed one question
    const percentage = Math.round((score / total) * 100);
    const incorrectIndices = [total - 1];

    quizResults[lessonId] = {
      lessonId,
      score,
      total,
      percentage,
      incorrectQuestionIndices: incorrectIndices,
      date: dayOffset(-2),
    };
    incorrectQuestions[lessonId] = incorrectIndices;

    // Unlock next lesson in sequence
    const idx = all.findIndex((a) => a.lesson.id === lessonId);
    if (idx + 1 < all.length) {
      const next = all[idx + 1].lesson.id;
      if (!unlockedLessons.includes(next)) unlockedLessons.push(next);
    }

    // Quiz cards: learned 4 days ago, one wrong answer
    item.lesson.quiz.forEach((_q, qi) => {
      const cardId = buildCardId(lessonId, qi);
      const wasCorrect = !incorrectIndices.includes(qi);
      if (wasCorrect) {
        // Correct once: box 2, interval 3 days, due today (quiz was 2 days ago + 3 = tomorrow... but we want due today)
        cardStates[cardId] = cardState(2, 1, 2, -1);
      } else {
        // Wrong: box 1, due today
        cardStates[cardId] = cardState(1, 0, 2, -1);
      }
    });

    // Flashcard cards: due today
    item.lesson.flashcards.forEach((_fc, fi) => {
      const cardId = buildCardId(lessonId, fi);
      cardStates[cardId] = cardState(2, 1, 2, -1);
    });
  }

  // --- Third difficulty-2 lesson: flashcards seen yesterday, quiz NOT done yet ---
  if (difficulty2.length > 2) {
    const item = difficulty2[2];
    const lessonId = item.lesson.id;
    firstLearnedDates[lessonId] = dayOffset(-1);
    reviewSessionDates[lessonId] = [dayOffset(-1)];
    // Quiz unlock date = firstLearned + 1 = today
    // Quiz not completed, so it shows as DUE today
  }

  // --- Badges ---
  const earnedBadges = ['first-lesson', 'quick-learner'];
  const hasPerfect = Object.values(quizResults).some((r) => r.percentage === 100);
  if (hasPerfect) earnedBadges.push('perfect-score');

  // Check category completion (only if ALL lessons in category are done, not just difficulty-1)
  const allClassroom = all.filter((item) => item.category.id === 'classroom-teachers');
  if (allClassroom.every((item) => completedLessons.includes(item.lesson.id))) {
    earnedBadges.push('classroom-ready');
  }

  const allSchool = all.filter((item) => item.category.id === 'school-systems');
  if (allSchool.every((item) => completedLessons.includes(item.lesson.id))) {
    earnedBadges.push('assignment-expert');
  }

  const lastLessonId = difficulty2.length > 2 ? difficulty2[2].lesson.id : difficulty2[0].lesson.id;

  return {
    completedLessons,
    unlockedLessons: Array.from(new Set(unlockedLessons)),
    quizResults,
    earnedBadges,
    lastLessonId,
    incorrectQuestions,
    cardStates,
    firstLearnedDates,
    reviewSessionDates,
    quizCompletedDates,
  };
}
