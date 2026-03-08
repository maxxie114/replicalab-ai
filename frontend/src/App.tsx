import { Routes, Route } from 'react-router-dom';
import EpisodePage from '@/pages/EpisodePage';
import DashboardPage from '@/pages/DashboardPage';
import ComparePage from '@/pages/ComparePage';
import PolicyComparePage from '@/pages/PolicyComparePage';
import TrainingPage from '@/pages/TrainingPage';
import Header from '@/components/Header';
import { ToastProvider } from '@/components/Toast';
import Onboarding, { useOnboarding } from '@/components/Onboarding';

export default function App() {
  const { showOnboarding, dismissOnboarding, resetOnboarding } = useOnboarding();

  return (
    <ToastProvider>
      <div className="min-h-screen bg-background text-foreground">
        <Header onShowTutorial={resetOnboarding} />
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/episode" element={<EpisodePage />} />
          <Route path="/episode/:episodeId" element={<EpisodePage />} />
          <Route path="/training" element={<TrainingPage />} />
          <Route path="/compare" element={<ComparePage />} />
          <Route path="/policies" element={<PolicyComparePage />} />
        </Routes>
        <Onboarding show={showOnboarding} onDismiss={dismissOnboarding} />
      </div>
    </ToastProvider>
  );
}
