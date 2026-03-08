import { Routes, Route } from 'react-router-dom';
import EpisodePage from '@/pages/EpisodePage';
import DashboardPage from '@/pages/DashboardPage';
import Header from '@/components/Header';

export default function App() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <Header />
      <Routes>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/episode" element={<EpisodePage />} />
        <Route path="/episode/:episodeId" element={<EpisodePage />} />
      </Routes>
    </div>
  );
}
