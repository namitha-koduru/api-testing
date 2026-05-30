import { Outlet } from 'react-router-dom';
import { Navbar } from '../components/layout/Navbar';
import { AIAssistant } from '../components/ai/AIAssistant';

export function MainLayout() {
  return (
    <div className="min-h-screen">
      <Navbar />
      <main className="pt-16 pb-20">
        <Outlet />
      </main>
      <AIAssistant />
    </div>
  );
}
