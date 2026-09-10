import { useState, useRef, useEffect } from 'react';
import { useRouter } from '@/context/RouterContext';
import { useProgress } from '@/context/ProgressContext';
import { Icon } from '@/components/ui/Icon';
import { LayoutDashboard, BookOpen, Trophy, Sparkles, Globe, Check, ChevronDown } from 'lucide-react';

const LANGUAGES = [
  'Arabic',
  'Chinese',
  'French',
  'German',
  'Hindi',
  'Portuguese',
  'Spanish',
];

function LanguageSelector() {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    function handleClickOutside(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    function handleEscape(e: KeyboardEvent) {
      if (e.key === 'Escape') setOpen(false);
    }
    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('keydown', handleEscape);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleEscape);
    };
  }, [open]);

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setOpen((o) => !o)}
        className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl text-sm font-semibold text-slate-600 hover:bg-slate-100 transition-colors duration-200"
        aria-label="Select language"
        aria-expanded={open}
      >
        <Globe size={18} className="text-slate-500" />
        <span className="hidden sm:inline">English</span>
        <ChevronDown size={14} className={`text-slate-400 transition-transform duration-200 ${open ? 'rotate-180' : ''}`} />
      </button>

      {open && (
        <div className="absolute right-0 mt-2 w-44 bg-white rounded-xl border border-slate-200 shadow-lg py-1 z-50">
          <div className="flex items-center justify-between px-3 py-2 text-sm font-semibold text-slate-800 hover:bg-slate-50 cursor-default">
            <span className="flex items-center gap-2">
              <Globe size={14} className="text-primary-500" />
              English
            </span>
            <Check size={16} className="text-primary-600" />
          </div>
          <div className="border-t border-slate-100 my-1" />
          {LANGUAGES.map((lang) => (
            <div
              key={lang}
              className="px-3 py-2 text-sm text-slate-600 hover:bg-slate-50 cursor-default"
            >
              {lang}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export function NavBar() {
  const router = useRouter();
  const { route } = router;
  const { demoMode, setDemoMode } = useProgress();

  const navItems = [
    { name: 'dashboard' as const, label: 'Dashboard', icon: LayoutDashboard },
    { name: 'lessons' as const, label: 'Lessons', icon: BookOpen },
    { name: 'progress' as const, label: 'Progress', icon: Trophy },
  ];

  return (
    <nav className="sticky top-0 z-50 bg-white/90 backdrop-blur-md border-b border-slate-200 shadow-sm">
      <div className="max-w-6xl mx-auto px-4 sm:px-6">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <button
            onClick={() => router.navigate({ name: 'dashboard' })}
            className="flex items-center gap-2 font-display font-bold text-lg text-primary-700"
          >
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center text-white">
              <Icon name="GraduationCap" size={20} />
            </div>
            <span className="hidden sm:inline">Campus Dutch</span>
          </button>

          {/* Nav links */}
          <div className="flex items-center gap-1 sm:gap-2">
            {navItems.map((item) => {
              const isActive = route.name === item.name ||
                (item.name === 'lessons' && (route.name === 'lesson' || route.name === 'quiz' || route.name === 'quiz-results'));
              const IconComp = item.icon;
              return (
                <button
                  key={item.name}
                  onClick={() => router.navigate({ name: item.name })}
                  className={`flex items-center gap-2 px-3 sm:px-4 py-2 rounded-xl font-semibold text-sm transition-all duration-200 ${
                    isActive
                      ? 'bg-primary-100 text-primary-700'
                      : 'text-slate-600 hover:bg-slate-100'
                  }`}
                  aria-current={isActive ? 'page' : undefined}
                >
                  <IconComp size={18} />
                  <span className="hidden sm:inline">{item.label}</span>
                </button>
              );
            })}
          </div>

          {/* Right side: language selector + demo mode */}
          <div className="flex items-center gap-2">
            <LanguageSelector />

            {demoMode && (
              <span className="flex items-center gap-1 text-xs font-bold px-2 py-1 rounded-full bg-accent-100 text-accent-700">
                <Sparkles size={12} /> Demo
              </span>
            )}
            <button
              onClick={() => setDemoMode(!demoMode)}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors duration-200 ${
                demoMode ? 'bg-accent-500' : 'bg-slate-300'
              }`}
              aria-label="Toggle demo mode"
              title="Demo Mode: unlock all lessons and quizzes for presentation"
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform duration-200 ${
                  demoMode ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}
