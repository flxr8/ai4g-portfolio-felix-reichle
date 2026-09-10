import { useRouter } from '@/context/RouterContext';
import { NavBar } from '@/components/NavBar';
import { Quiz } from '@/components/Quiz';
import { getLessonById } from '@/data/content';

interface QuizPageProps {
  lessonId: string;
  retryIncorrect?: boolean;
}

export function QuizPage({ lessonId, retryIncorrect }: QuizPageProps) {
  const router = useRouter();
  const lessonData = getLessonById(lessonId);

  if (!lessonData) {
    return (
      <div className="min-h-screen bg-slate-50">
        <NavBar />
        <div className="max-w-4xl mx-auto px-6 py-16 text-center">
          <h1 className="font-display text-2xl font-bold text-slate-700">Quiz not found</h1>
          <button onClick={() => router.navigate({ name: 'lessons' })} className="mt-6 text-primary-600 font-semibold">
            Back to Lessons
          </button>
        </div>
      </div>
    );
  }

  const incorrectIndices = retryIncorrect
    ? (JSON.parse(localStorage.getItem('campus-dutch-progress') || '{}').incorrectQuestions?.[lessonId] || [])
    : [];

  return (
    <div className="min-h-screen bg-slate-50">
      <NavBar />
      <div className="max-w-4xl mx-auto px-4 sm:px-6 py-8">
        <Quiz
          lessonId={lessonId}
          questions={lessonData.lesson.quiz}
          retryIncorrect={retryIncorrect}
          incorrectIndices={incorrectIndices}
        />
      </div>
    </div>
  );
}
