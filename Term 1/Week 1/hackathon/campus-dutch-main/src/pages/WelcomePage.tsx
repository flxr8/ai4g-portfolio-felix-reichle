import { useRouter } from '@/context/RouterContext';
import { Button } from '@/components/ui/Button';
import { Icon } from '@/components/ui/Icon';
import { GraduationCap, BookOpen, MessageCircle, Sparkles, ArrowRight } from 'lucide-react';

export function WelcomePage() {
  const router = useRouter();

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-accent-50 flex flex-col">
      {/* Decorative shapes */}
      <div className="absolute top-0 right-0 w-72 h-72 bg-primary-200/30 rounded-full blur-3xl -translate-y-1/4 translate-x-1/4" />
      <div className="absolute bottom-0 left-0 w-96 h-96 bg-accent-200/30 rounded-full blur-3xl translate-y-1/4 -translate-x-1/4" />

      {/* Content */}
      <div className="relative flex-1 flex flex-col items-center justify-center px-6 py-12 max-w-4xl mx-auto text-center">
        {/* Logo */}
        <div className="mb-8 animate-pop">
          <div className="w-20 h-20 rounded-3xl bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center text-white shadow-xl mx-auto">
            <GraduationCap size={40} />
          </div>
        </div>

        {/* Title */}
        <div className="animate-slide-up">
          <h1 className="font-display text-4xl sm:text-5xl md:text-6xl font-extrabold text-slate-800 mb-4">
            Campus Dutch
          </h1>
          <div className="flex items-center justify-center gap-2 text-primary-600 mb-6">
            <Sparkles size={20} />
            <span className="font-semibold text-lg">Learn Dutch for university life</span>
            <Sparkles size={20} />
          </div>
        </div>

        {/* Description */}
        <p className="text-lg text-slate-600 max-w-2xl leading-relaxed mb-10 animate-fade-in">
          Campus Dutch helps international students understand the Dutch words and instructions
          they may encounter at university. From grades and deadlines to classroom communication —
          learn at your own pace with flashcards and quizzes.
        </p>

        {/* Feature cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 w-full max-w-2xl mb-10">
          <div className="bg-white/70 backdrop-blur-sm rounded-2xl p-5 border border-primary-200 shadow-sm flex items-start gap-3 animate-slide-up">
            <div className="flex-shrink-0 w-10 h-10 rounded-xl bg-primary-100 flex items-center justify-center text-primary-600">
              <BookOpen size={20} />
            </div>
            <div className="text-left">
              <h3 className="font-display font-bold text-slate-800">School Systems</h3>
              <p className="text-sm text-slate-600 mt-1">Grades, deadlines, submissions and course platforms</p>
            </div>
          </div>
          <div className="bg-white/70 backdrop-blur-sm rounded-2xl p-5 border border-accent-200 shadow-sm flex items-start gap-3 animate-slide-up">
            <div className="flex-shrink-0 w-10 h-10 rounded-xl bg-accent-100 flex items-center justify-center text-accent-600">
              <MessageCircle size={20} />
            </div>
            <div className="text-left">
              <h3 className="font-display font-bold text-slate-800">Classroom & Teachers</h3>
              <p className="text-sm text-slate-600 mt-1">Instructions, asking questions and talking to lecturers</p>
            </div>
          </div>
        </div>

        {/* CTA */}
        <Button
          variant="primary"
          size="lg"
          onClick={() => router.navigate({ name: 'dashboard' })}
          className="animate-pop"
        >
          Start Learning
          <ArrowRight size={22} />
        </Button>

        <p className="mt-6 text-sm text-slate-400">No account needed — your progress is saved on this device</p>
      </div>
    </div>
  );
}
