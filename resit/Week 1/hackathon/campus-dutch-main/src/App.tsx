import { ProgressProvider } from '@/context/ProgressContext';
import { RouterProvider, useRouter } from '@/context/RouterContext';
import { WelcomePage } from '@/pages/WelcomePage';
import { DashboardPage } from '@/pages/DashboardPage';
import { LessonsOverviewPage } from '@/pages/LessonsOverviewPage';
import { LessonPage } from '@/pages/LessonPage';
import { QuizPage } from '@/pages/QuizPage';
import { QuizResultsPage } from '@/pages/QuizResultsPage';
import { ProgressPage } from '@/pages/ProgressPage';
import { ReviewPage } from '@/pages/ReviewPage';

function RouteRenderer() {
  const { route } = useRouter();

  switch (route.name) {
    case 'welcome':
      return <WelcomePage />;
    case 'dashboard':
      return <DashboardPage />;
    case 'lessons':
      return <LessonsOverviewPage />;
    case 'lesson':
      return <LessonPage lessonId={route.lessonId} />;
    case 'quiz':
      return <QuizPage lessonId={route.lessonId} retryIncorrect={route.retryIncorrect} />;
    case 'quiz-results':
      return (
        <QuizResultsPage
          lessonId={route.lessonId}
          score={route.score}
          total={route.total}
          incorrectIndices={route.incorrectIndices}
          retryIncorrect={route.retryIncorrect}
        />
      );
    case 'progress':
      return <ProgressPage />;
    case 'review':
      return <ReviewPage />;
    default:
      return <WelcomePage />;
  }
}

function App() {
  return (
    <ProgressProvider>
      <RouterProvider>
        <RouteRenderer />
      </RouterProvider>
    </ProgressProvider>
  );
}

export default App;
