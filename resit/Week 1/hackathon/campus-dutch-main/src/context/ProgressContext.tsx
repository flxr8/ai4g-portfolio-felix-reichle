import { createContext, useContext, useEffect, useState, useCallback, useRef, type ReactNode } from 'react';
import { categories, badges, getAllLessons, getLessonById } from '@/data/content';
import {
  type CardStateMap,
  defaultCardState,
  answerCorrect,
  answerIncorrect,
  todayISO,
  isSameDay,
  buildCardId,
} from '@/data/leitner';
import { buildDemoState } from '@/data/demoMockData';

export interface QuizResult {
  lessonId: string;
  score: number;
  total: number;
  percentage: number;
  incorrectQuestionIndices: number[];
  date: string;
}

export interface ProgressState {
  completedLessons: string[];
  unlockedLessons: string[];
  quizResults: Record<string, QuizResult>;
  earnedBadges: string[];
  lastLessonId: string | null;
  incorrectQuestions: Record<string, number[]>;
  cardStates: CardStateMap;
  firstLearnedDates: Record<string, string>;
  reviewSessionDates: Record<string, string[]>;
  quizCompletedDates: Record<string, string>;
}

const STORAGE_KEY = 'campus-dutch-progress';
const DEMO_KEY = 'campus-dutch-demo';

const initialState: ProgressState = {
  completedLessons: [],
  unlockedLessons: ['grades-l1', 'deadlines-l1', 'platforms-l1', 'classroom-l1', 'talking-l1', 'asking-l1'],
  quizResults: {},
  earnedBadges: [],
  lastLessonId: null,
  incorrectQuestions: {},
  cardStates: {},
  firstLearnedDates: {},
  reviewSessionDates: {},
  quizCompletedDates: {},
};

function loadState(): ProgressState {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return initialState;
    const parsed = JSON.parse(raw) as Partial<ProgressState>;
    return {
      ...initialState,
      ...parsed,
      unlockedLessons: Array.from(
        new Set([...initialState.unlockedLessons, ...(parsed.unlockedLessons || [])])
      ),
      cardStates: parsed.cardStates || {},
      firstLearnedDates: parsed.firstLearnedDates || {},
      reviewSessionDates: parsed.reviewSessionDates || {},
      quizCompletedDates: parsed.quizCompletedDates || {},
      incorrectQuestions: parsed.incorrectQuestions || {},
    };
  } catch {
    return initialState;
  }
}

export interface DueQuiz {
  lessonId: string;
  title: string;
  firstLearnedDate: string;
  dueDate: string;
}

interface ProgressContextValue {
  state: ProgressState;
  demoMode: boolean;
  setDemoMode: (on: boolean) => void;
  recordQuizResult: (result: QuizResult) => void;
  resetProgress: () => void;
  isLessonUnlocked: (lessonId: string) => boolean;
  isLessonCompleted: (lessonId: string) => boolean;
  getOverallProgress: () => { completed: number; total: number; percentage: number };
  getCategoryProgress: (categoryId: string) => { completed: number; total: number; percentage: number };
  getRecommendedLesson: () => { lessonId: string; title: string; categoryId: string } | null;
  newlyEarnedBadges: string[];
  clearNewBadges: () => void;
  recordCardAnswer: (cardId: string, correct: boolean) => void;
  recordFlashcardReview: (lessonId: string) => void;
  getLessonStage: (lessonId: string) => 'not-started' | 'learning' | 'in-review';
  isQuizUnlocked: (lessonId: string) => boolean;
  getQuizUnlockDate: (lessonId: string) => string | null;
  getDueQuizzes: () => DueQuiz[];
  getDueQuizCount: () => number;
}

const ProgressContext = createContext<ProgressContextValue | null>(null);

export function ProgressProvider({ children }: { children: ReactNode }) {
  const [realState, setRealState] = useState<ProgressState>(loadState);
  const [demoState, setDemoState] = useState<ProgressState>(() => buildDemoState());
  const [newlyEarnedBadges, setNewlyEarnedBadges] = useState<string[]>([]);
  const [demoMode, setDemoModeState] = useState<boolean>(() => {
    try {
      return localStorage.getItem(DEMO_KEY) === 'true';
    } catch {
      return false;
    }
  });

  // Only persist real state to localStorage — demo state is ephemeral
  useEffect(() => {
    if (demoMode) return;
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(realState));
    } catch {
      // ignore storage errors
    }
  }, [realState, demoMode]);

  const state = demoMode ? demoState : realState;
  const setState = demoMode ? setDemoState : setRealState;

  // Keep a ref so setDemoMode can rebuild demo state on enable
  const demoModeRef = useRef(demoMode);
  demoModeRef.current = demoMode;

  const setDemoMode = useCallback((on: boolean) => {
    setDemoModeState(on);
    try {
      if (on) {
        localStorage.setItem(DEMO_KEY, 'true');
        // Rebuild fresh demo state every time demo mode is turned on
        setDemoState(buildDemoState());
      } else {
        localStorage.removeItem(DEMO_KEY);
      }
    } catch {
      // ignore
    }
    setNewlyEarnedBadges([]);
  }, []);

  const checkAndAwardBadges = useCallback((newState: ProgressState): string[] => {
    const earned = new Set(newState.earnedBadges);
    const newBadges: string[] = [];

    const allLessons = getAllLessons();
    const completedSet = new Set(newState.completedLessons);

    if (completedSet.size >= 1 && !earned.has('first-lesson')) {
      earned.add('first-lesson');
      newBadges.push('first-lesson');
    }

    const hasHighScore = Object.values(newState.quizResults).some((r) => r.percentage >= 80);
    if (hasHighScore && !earned.has('quick-learner')) {
      earned.add('quick-learner');
      newBadges.push('quick-learner');
    }

    const hasPerfectScore = Object.values(newState.quizResults).some((r) => r.percentage === 100);
    if (hasPerfectScore && !earned.has('perfect-score')) {
      earned.add('perfect-score');
      newBadges.push('perfect-score');
    }

    const classroomCategory = categories.find((c) => c.id === 'classroom-teachers');
    if (classroomCategory) {
      const classroomLessons = classroomCategory.topics.flatMap((t) => t.lessons);
      const allClassroomDone = classroomLessons.every((l) => completedSet.has(l.id));
      if (allClassroomDone && !earned.has('classroom-ready')) {
        earned.add('classroom-ready');
        newBadges.push('classroom-ready');
      }
    }

    const schoolCategory = categories.find((c) => c.id === 'school-systems');
    if (schoolCategory) {
      const schoolLessons = schoolCategory.topics.flatMap((t) => t.lessons);
      const allSchoolDone = schoolLessons.every((l) => completedSet.has(l.id));
      if (allSchoolDone && !earned.has('assignment-expert')) {
        earned.add('assignment-expert');
        newBadges.push('assignment-expert');
      }
    }

    const allDone = allLessons.every((item) => completedSet.has(item.lesson.id));
    if (allDone && !earned.has('campus-champion')) {
      earned.add('campus-champion');
      newBadges.push('campus-champion');
    }

    return newBadges;
  }, []);

  const recordCardAnswer = useCallback((cardId: string, correct: boolean) => {
    setState((prev) => {
      const prevCardState = prev.cardStates[cardId] || defaultCardState();
      const newCardState = correct ? answerCorrect(prevCardState) : answerIncorrect(prevCardState);
      return {
        ...prev,
        cardStates: { ...prev.cardStates, [cardId]: newCardState },
      };
    });
  }, [setState]);

  const recordFlashcardReview = useCallback((lessonId: string) => {
    setState((prev) => {
      const today = todayISO();
      const existing = prev.firstLearnedDates[lessonId];
      const firstLearned = existing || today;

      const reviewDates = prev.reviewSessionDates[lessonId] || [];
      if (!reviewDates.includes(today)) {
        reviewDates.push(today);
      }

      return {
        ...prev,
        firstLearnedDates: { ...prev.firstLearnedDates, [lessonId]: firstLearned },
        reviewSessionDates: { ...prev.reviewSessionDates, [lessonId]: reviewDates },
      };
    });
  }, [setState]);

  const recordQuizResult = useCallback(
    (result: QuizResult) => {
      setState((prev) => {
        const today = todayISO();
        const newCompleted = prev.completedLessons.includes(result.lessonId)
          ? prev.completedLessons
          : [...prev.completedLessons, result.lessonId];

        const newUnlocked = [...prev.unlockedLessons];
        const lessonData = getLessonById(result.lessonId);
        if (lessonData) {
          const allLessons = getAllLessons();
          const idx = allLessons.findIndex((item) => item.lesson.id === result.lessonId);
          if (result.percentage >= 80 && idx + 1 < allLessons.length) {
            const nextLesson = allLessons[idx + 1].lesson;
            if (!newUnlocked.includes(nextLesson.id)) {
              newUnlocked.push(nextLesson.id);
            }
          }
          if (result.percentage >= 60) {
            for (const item of allLessons) {
              if (
                item.category.id === lessonData.category.id &&
                item.lesson.difficulty === lessonData.lesson.difficulty &&
                !newUnlocked.includes(item.lesson.id)
              ) {
                newUnlocked.push(item.lesson.id);
              }
            }
          }

          const newCardStates = { ...prev.cardStates };
          lessonData.lesson.quiz.forEach((q, qi) => {
            const cardId = buildCardId(result.lessonId, qi);
            const prevCardState = newCardStates[cardId] || defaultCardState();
            const wasCorrect = !result.incorrectQuestionIndices.includes(qi);
            newCardStates[cardId] = wasCorrect ? answerCorrect(prevCardState) : answerIncorrect(prevCardState);
          });
        }

        const newIncorrect: Record<string, number[]> = { ...prev.incorrectQuestions };
        if (result.incorrectQuestionIndices.length > 0) {
          newIncorrect[result.lessonId] = result.incorrectQuestionIndices;
        } else {
          delete newIncorrect[result.lessonId];
        }

        const newState: ProgressState = {
          ...prev,
          completedLessons: newCompleted,
          unlockedLessons: Array.from(new Set(newUnlocked)),
          quizResults: {
            ...prev.quizResults,
            [result.lessonId]: result,
          },
          lastLessonId: result.lessonId,
          incorrectQuestions: newIncorrect,
          firstLearnedDates: {
            ...prev.firstLearnedDates,
            [result.lessonId]: prev.firstLearnedDates[result.lessonId] || today,
          },
          quizCompletedDates: {
            ...prev.quizCompletedDates,
            [result.lessonId]: today,
          },
        };

        const newBadges = checkAndAwardBadges(newState);
        if (newBadges.length > 0) {
          newState.earnedBadges = [...new Set([...newState.earnedBadges, ...newBadges])];
          setNewlyEarnedBadges(newBadges);
        }

        return newState;
      });
    },
    [checkAndAwardBadges, setState]
  );

  const resetProgress = useCallback(() => {
    if (demoModeRef.current) {
      setDemoState(buildDemoState());
    } else {
      setRealState(initialState);
      try {
        localStorage.removeItem(STORAGE_KEY);
      } catch {
        // ignore
      }
    }
    setNewlyEarnedBadges([]);
  }, []);

  const isLessonUnlocked = useCallback(
    (lessonId: string) => state.unlockedLessons.includes(lessonId),
    [state.unlockedLessons]
  );

  const isLessonCompleted = useCallback(
    (lessonId: string) => state.completedLessons.includes(lessonId),
    [state.completedLessons]
  );

  const getOverallProgress = useCallback(() => {
    const all = getAllLessons();
    const completed = all.filter((item) => state.completedLessons.includes(item.lesson.id)).length;
    const total = all.length;
    return {
      completed,
      total,
      percentage: total > 0 ? Math.round((completed / total) * 100) : 0,
    };
  }, [state.completedLessons]);

  const getCategoryProgress = useCallback(
    (categoryId: string) => {
      const category = categories.find((c) => c.id === categoryId);
      if (!category) return { completed: 0, total: 0, percentage: 0 };
      const lessons = category.topics.flatMap((t) => t.lessons);
      const completed = lessons.filter((l) => state.completedLessons.includes(l.id)).length;
      const total = lessons.length;
      return {
        completed,
        total,
        percentage: total > 0 ? Math.round((completed / total) * 100) : 0,
      };
    },
    [state.completedLessons]
  );

  const getRecommendedLesson = useCallback(() => {
    const all = getAllLessons();
    if (state.lastLessonId) {
      const idx = all.findIndex((item) => item.lesson.id === state.lastLessonId);
      if (idx !== -1 && idx + 1 < all.length) {
        const next = all[idx + 1];
        if (state.unlockedLessons.includes(next.lesson.id)) {
          return { lessonId: next.lesson.id, title: next.lesson.title, categoryId: next.category.id };
        }
      }
    }
    const next = all.find(
      (item) =>
        state.unlockedLessons.includes(item.lesson.id) &&
        !state.completedLessons.includes(item.lesson.id)
    );
    if (next) return { lessonId: next.lesson.id, title: next.lesson.title, categoryId: next.category.id };
    return null;
  }, [state.lastLessonId, state.unlockedLessons, state.completedLessons]);

  const getLessonStage = useCallback((lessonId: string): 'not-started' | 'learning' | 'in-review' => {
    const lessonData = getLessonById(lessonId);
    if (!lessonData) return 'not-started';
    const hasFirstLearned = !!state.firstLearnedDates[lessonId];
    const reviewDates = state.reviewSessionDates[lessonId] || [];
    if (!hasFirstLearned && reviewDates.length === 0) return 'not-started';
    if (reviewDates.length <= 1) return 'learning';
    return 'in-review';
  }, [state.firstLearnedDates, state.reviewSessionDates]);

  const getQuizUnlockDate = useCallback((lessonId: string): string | null => {
    const firstLearned = state.firstLearnedDates[lessonId];
    if (!firstLearned) return null;
    try {
      const [y, m, d] = firstLearned.split('-').map(Number);
      if (isNaN(y) || isNaN(m) || isNaN(d)) return null;
      const date = new Date(y, m - 1, d);
      date.setDate(date.getDate() + 1);
      const uy = date.getFullYear();
      const um = String(date.getMonth() + 1).padStart(2, '0');
      const ud = String(date.getDate()).padStart(2, '0');
      return `${uy}-${um}-${ud}`;
    } catch {
      return null;
    }
  }, [state.firstLearnedDates]);

  const isQuizUnlocked = useCallback(
    (lessonId: string): boolean => {
      const lessonData = getLessonById(lessonId);
      if (!lessonData) return false;
      if (!state.unlockedLessons.includes(lessonId)) return false;
      const unlockDate = getQuizUnlockDate(lessonId);
      if (!unlockDate) return false;
      return todayISO() >= unlockDate;
    },
    [state.unlockedLessons, getQuizUnlockDate, state.firstLearnedDates]
  );

  const getDueQuizzes = useCallback((): DueQuiz[] => {
    const all = getAllLessons();
    const today = todayISO();
    const due: DueQuiz[] = [];
    for (const item of all) {
      const lessonId = item.lesson.id;
      const firstLearned = state.firstLearnedDates[lessonId];
      if (!firstLearned) continue;
      const unlockDate = getQuizUnlockDate(lessonId);
      if (!unlockDate) continue;
      const quizDoneDate = state.quizCompletedDates[lessonId];
      const quizDoneToday = quizDoneDate && isSameDay(quizDoneDate, today);
      if (today >= unlockDate && !quizDoneToday) {
        due.push({
          lessonId,
          title: item.lesson.title,
          firstLearnedDate: firstLearned,
          dueDate: unlockDate,
        });
      }
    }
    return due;
  }, [state.firstLearnedDates, state.quizCompletedDates, getQuizUnlockDate]);

  const getDueQuizCount = useCallback(() => getDueQuizzes().length, [getDueQuizzes]);

  const clearNewBadges = useCallback(() => setNewlyEarnedBadges([]), []);

  return (
    <ProgressContext.Provider
      value={{
        state,
        demoMode,
        setDemoMode,
        recordQuizResult,
        resetProgress,
        isLessonUnlocked,
        isLessonCompleted,
        getOverallProgress,
        getCategoryProgress,
        getRecommendedLesson,
        newlyEarnedBadges,
        clearNewBadges,
        recordCardAnswer,
        recordFlashcardReview,
        getLessonStage,
        isQuizUnlocked,
        getQuizUnlockDate,
        getDueQuizzes,
        getDueQuizCount,
      }}
    >
      {children}
    </ProgressContext.Provider>
  );
}

export function useProgress() {
  const ctx = useContext(ProgressContext);
  if (!ctx) throw new Error('useProgress must be used within ProgressProvider');
  return ctx;
}

export { badges };
