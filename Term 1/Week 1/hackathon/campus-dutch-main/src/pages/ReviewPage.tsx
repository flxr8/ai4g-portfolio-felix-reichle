import { useRouter } from '@/context/RouterContext';
import { useProgress } from '@/context/ProgressContext';
import { NavBar } from '@/components/NavBar';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { ArrowLeft, CheckCircle2, Clock, ArrowRight } from 'lucide-react';

export function ReviewPage() {
  const router = useRouter();
  const { getDueQuizzes } = useProgress();

  const dueQuizzes = getDueQuizzes();

  if (dueQuizzes.length === 0) {
    return (
      <div className="min-h-screen bg-slate-50">
        <NavBar />
        <div className="max-w-4xl mx-auto px-4 sm:px-6 py-8">
          <button
            onClick={() => router.navigate({ name: 'dashboard' })}
            className="flex items-center gap-2 text-slate-500 hover:text-slate-700 font-semibold text-sm mb-6 transition-colors"
          >
            <ArrowLeft size={18} /> Back to Dashboard
          </button>
          <Card className="p-12 text-center">
            <div className="w-20 h-20 rounded-full bg-success-100 flex items-center justify-center text-success-600 mx-auto mb-6">
              <CheckCircle2 size={40} />
            </div>
            <h1 className="font-display text-2xl font-bold text-slate-800 mb-3">
              You're all caught up!
            </h1>
            <p className="text-slate-600 mb-6 max-w-md mx-auto">
              No quizzes are due for review right now. Come back tomorrow to keep building your Dutch vocabulary.
            </p>
            <Button variant="primary" size="md" onClick={() => router.navigate({ name: 'dashboard' })}>
              Back to Dashboard
            </Button>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <NavBar />
      <div className="max-w-4xl mx-auto px-4 sm:px-6 py-8">
        <button
          onClick={() => router.navigate({ name: 'dashboard' })}
          className="flex items-center gap-2 text-slate-500 hover:text-slate-700 font-semibold text-sm mb-6 transition-colors"
        >
          <ArrowLeft size={18} /> Back to Dashboard
        </button>

        <div className="flex items-center gap-3 mb-8">
          <div className="w-10 h-10 rounded-xl bg-primary-100 flex items-center justify-center text-primary-600">
            <Clock size={20} />
          </div>
          <div>
            <h1 className="font-display text-2xl font-bold text-slate-800">Today's Review</h1>
            <p className="text-sm text-slate-500">
              {dueQuizzes.length} quiz{dueQuizzes.length !== 1 ? 'zes' : ''} due for review
            </p>
          </div>
        </div>

        <div className="space-y-3">
          {dueQuizzes.map((quiz) => (
            <Card
              key={quiz.lessonId}
              className="p-5 border-primary-200 bg-gradient-to-r from-primary-50 to-white"
              interactive
              onClick={() => router.navigate({ name: 'lesson', lessonId: quiz.lessonId })}
            >
              <div className="flex items-center justify-between gap-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-primary-500 flex items-center justify-center text-white">
                    <Clock size={20} />
                  </div>
                  <div>
                    <p className="font-display font-bold text-base text-slate-800">{quiz.title}</p>
                    <p className="text-xs text-slate-500">Due since {quiz.dueDate}</p>
                  </div>
                </div>
                <Button variant="primary" size="sm">
                  Review <ArrowRight size={16} />
                </Button>
              </div>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}
