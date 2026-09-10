import type { Flashcard, QuizQuestion } from '@/data/content';

export interface CardState {
  box: number;
  nextReviewDate: string;
  correctStreak: number;
  timesSeen: number;
}

export type CardStateMap = Record<string, CardState>;

export const BOX_INTERVALS = [1, 3, 7, 14, 30];

export function localDateStr(d: Date = new Date()): string {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
}

export function todayISO(): string {
  return localDateStr();
}

export function daysFromToday(days: number): string {
  const d = new Date();
  d.setDate(d.getDate() + days);
  return localDateStr(d);
}

export function tomorrowISO(): string {
  return daysFromToday(1);
}

export function isSameDay(dateA: string, dateB: string): boolean {
  return dateA === dateB;
}

export function isDue(nextReviewDate: string, refDate: string = todayISO()): boolean {
  return nextReviewDate <= refDate;
}

export function isAfter(dateA: string, dateB: string): boolean {
  return dateA > dateB;
}

export function defaultCardState(): CardState {
  return {
    box: 1,
    nextReviewDate: todayISO(),
    correctStreak: 0,
    timesSeen: 0,
  };
}

export function answerCorrect(prev: CardState): CardState {
  const newBox = Math.min(prev.box + 1, 5);
  const newStreak = prev.correctStreak + 1;
  const interval = BOX_INTERVALS[newBox - 1];
  return {
    box: newBox,
    nextReviewDate: daysFromToday(interval),
    correctStreak: newStreak,
    timesSeen: prev.timesSeen + 1,
  };
}

export function answerIncorrect(prev: CardState): CardState {
  return {
    box: 1,
    nextReviewDate: daysFromToday(1),
    correctStreak: 0,
    timesSeen: prev.timesSeen + 1,
  };
}

export interface CardWithMeta extends Flashcard {
  cardId: string;
  lessonId: string;
}

export interface QuizCardWithMeta extends QuizQuestion {
  cardId: string;
  lessonId: string;
  originalIndex: number;
}

export function buildCardId(lessonId: string, index: number): string {
  return `${lessonId}::${index}`;
}

export function isCardMastered(state: CardState): boolean {
  return state.correctStreak >= 3;
}

export function shuffle<T>(arr: T[]): T[] {
  const result = [...arr];
  for (let i = result.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [result[i], result[j]] = [result[j], result[i]];
  }
  return result;
}

export function formatDateDisplay(dateStr: string): string {
  try {
    const [y, m, d] = dateStr.split('-').map(Number);
    const date = new Date(y, m - 1, d);
    return date.toLocaleDateString(undefined, { weekday: 'long', month: 'short', day: 'numeric' });
  } catch {
    return dateStr;
  }
}
