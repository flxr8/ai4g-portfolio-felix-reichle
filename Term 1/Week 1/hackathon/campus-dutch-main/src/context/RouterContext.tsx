import { createContext, useContext, useEffect, useState, useCallback, type ReactNode } from 'react';

export type Route =
  | { name: 'welcome' }
  | { name: 'dashboard' }
  | { name: 'lessons' }
  | { name: 'lesson'; lessonId: string }
  | { name: 'quiz'; lessonId: string; retryIncorrect?: boolean }
  | { name: 'quiz-results'; lessonId: string; score: number; total: number; incorrectIndices: string; retryIncorrect?: boolean }
  | { name: 'progress' }
  | { name: 'review' };

interface RouterContextValue {
  route: Route;
  navigate: (route: Route) => void;
  goBack: () => void;
  canGoBack: boolean;
}

const RouterContext = createContext<RouterContextValue | null>(null);

function parseHash(): Route {
  const hash = window.location.hash.replace(/^#\/?/, '');
  const parts = hash.split('/').filter(Boolean);

  if (parts.length === 0) return { name: 'welcome' };

  switch (parts[0]) {
    case 'dashboard':
      return { name: 'dashboard' };
    case 'lessons':
      if (parts.length >= 2) return { name: 'lesson', lessonId: parts[1] };
      return { name: 'lessons' };
    case 'quiz':
      if (parts.length >= 3 && parts[2] === 'results') {
        return {
          name: 'quiz-results',
          lessonId: parts[1],
          score: Number(parts[3] || 0),
          total: Number(parts[4] || 0),
          incorrectIndices: parts[5] || '',
          retryIncorrect: parts[6] === 'retry',
        };
      }
      if (parts.length >= 2) {
        return { name: 'quiz', lessonId: parts[1], retryIncorrect: parts[2] === 'retry' };
      }
      return { name: 'dashboard' };
    case 'progress':
      return { name: 'progress' };
    case 'review':
      return { name: 'review' };
    default:
      return { name: 'welcome' };
  }
}

function routeToHash(route: Route): string {
  switch (route.name) {
    case 'welcome':
      return '#/';
    case 'dashboard':
      return '#/dashboard';
    case 'lessons':
      return '#/lessons';
    case 'lesson':
      return `#/lessons/${route.lessonId}`;
    case 'quiz':
      return route.retryIncorrect
        ? `#/quiz/${route.lessonId}/retry`
        : `#/quiz/${route.lessonId}`;
    case 'quiz-results':
      return `#/quiz/${route.lessonId}/results/${route.score}/${route.total}/${route.incorrectIndices}${route.retryIncorrect ? '/retry' : ''}`;
    case 'progress':
      return '#/progress';
    case 'review':
      return '#/review';
    default:
      return '#/';
  }
}

export function RouterProvider({ children }: { children: ReactNode }) {
  const [route, setRoute] = useState<Route>(parseHash);
  const [history, setHistory] = useState<string[]>([window.location.hash]);

  useEffect(() => {
    const handler = () => {
      setRoute(parseHash());
      setHistory((prev) => [...prev, window.location.hash]);
    };
    window.addEventListener('hashchange', handler);
    return () => window.removeEventListener('hashchange', handler);
  }, []);

  const navigate = useCallback((newRoute: Route) => {
    const hash = routeToHash(newRoute);
    window.location.hash = hash;
  }, []);

  const goBack = useCallback(() => {
    window.history.back();
  }, []);

  return (
    <RouterContext.Provider value={{ route, navigate, goBack, canGoBack: history.length > 1 }}>
      {children}
    </RouterContext.Provider>
  );
}

export function useRouter() {
  const ctx = useContext(RouterContext);
  if (!ctx) throw new Error('useRouter must be used within RouterProvider');
  return ctx;
}
