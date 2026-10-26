import React, { useState, useEffect } from 'react';
import {
  LayoutDashboard,
  Film,
  FileText,
  UserCheck,
  DollarSign,
  Settings,
  RefreshCw,
  Sparkles
} from 'lucide-react';
import { YouTubeIcon } from './components/YouTubeIcon';
import { Header } from './components/Header';
import { MonthlyTracker } from './components/MonthlyTracker';
import { PipelineOverview } from './components/PipelineOverview';
import { VideoLibrary } from './components/VideoLibrary';
import { TopicScriptManager } from './components/TopicScriptManager';
import { CharacterStudio } from './components/CharacterStudio';
import { YouTubeManager } from './components/YouTubeManager';
import { MonetisationView } from './components/MonetisationView';
import { SettingsModal } from './components/SettingsModal';
import { DashboardStats, TopicItem, ScriptItem, VideoItem } from './types';
import { api } from './api';

export const App: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [topics, setTopics] = useState<TopicItem[]>([]);
  const [scripts, setScripts] = useState<ScriptItem[]>([]);
  const [videos, setVideos] = useState<VideoItem[]>([]);
  const [activeTab, setActiveTab] = useState<'overview' | 'videos' | 'scripts' | 'studio' | 'youtube' | 'monetisation'>('overview');
  const [isSettingsOpen, setIsSettingsOpen] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const loadData = async () => {
    try {
      const [sData, tData, scrData, vData] = await Promise.all([
        api.getDashboardStats().catch(() => null),
        api.getTopics().catch(() => []),
        api.getScripts().catch(() => []),
        api.getVideos().catch(() => [])
      ]);
      if (sData) setStats(sData);
      setTopics(tData);
      setScripts(scrData);
      setVideos(vData);
    } catch (e) {
      console.error('Error refreshing dashboard:', e);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleRunCycle = async () => {
    try {
      setIsLoading(true);
      await api.runCycle();
      await loadData();
    } catch (e: any) {
      alert(e.message || 'Failed to trigger cycle');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDiscoverTopics = async () => {
    try {
      setIsLoading(true);
      await api.discoverTopics(3);
      await loadData();
    } catch (e: any) {
      alert(e.message || 'Failed to discover topics');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateScript = async (topicId: string) => {
    try {
      setIsLoading(true);
      await api.generateScript(topicId);
      await loadData();
      setActiveTab('scripts');
    } catch (e: any) {
      alert(e.message || 'Failed to generate script');
    } finally {
      setIsLoading(false);
    }
  };

  const handleProduceVideo = async (scriptId: string) => {
    try {
      setIsLoading(true);
      await api.produceVideo(scriptId);
      await loadData();
      setActiveTab('videos');
    } catch (e: any) {
      alert(e.message || 'Failed to produce video');
    } finally {
      setIsLoading(false);
    }
  };

  const handleToggleScheduler = async () => {
    if (!stats) return;
    const nextState = !stats.system_status.autonomous_scheduler_active;
    try {
      await api.toggleScheduler(nextState);
      await loadData();
    } catch (e: any) {
      alert(e.message);
    }
  };

  const handleToggleKillswitch = async () => {
    if (!stats) return;
    const nextState = !stats.system_status.killswitch_active;
    try {
      await api.toggleKillswitch(nextState);
      await loadData();
    } catch (e: any) {
      alert(e.message);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#07090e] text-slate-100 font-sans">
      {/* Top HUD Header */}
      <Header
        stats={stats}
        onToggleScheduler={handleToggleScheduler}
        onToggleKillswitch={handleToggleKillswitch}
        onRunCycle={handleRunCycle}
        isLoading={isLoading}
      />

      {/* Main Command Center Body */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 md:p-6 space-y-6">
        
        {/* Navigation Bar */}
        <div className="flex items-center justify-between border-b border-slate-800/80 pb-2 overflow-x-auto">
          <nav className="flex items-center gap-1.5 min-w-max">
            <button
              onClick={() => setActiveTab('overview')}
              className={`px-3.5 py-2 rounded-xl text-xs font-semibold flex items-center gap-2 transition-all ${
                activeTab === 'overview'
                  ? 'bg-cyan-500/15 text-cyan-300 border border-cyan-500/40 shadow-sm shadow-cyan-500/20'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
              }`}
            >
              <LayoutDashboard className="w-4 h-4" />
              <span>Overview</span>
            </button>

            <button
              onClick={() => setActiveTab('videos')}
              className={`px-3.5 py-2 rounded-xl text-xs font-semibold flex items-center gap-2 transition-all ${
                activeTab === 'videos'
                  ? 'bg-cyan-500/15 text-cyan-300 border border-cyan-500/40 shadow-sm shadow-cyan-500/20'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
              }`}
            >
              <Film className="w-4 h-4" />
              <span>Video Vault ({videos.length})</span>
            </button>

            <button
              onClick={() => setActiveTab('scripts')}
              className={`px-3.5 py-2 rounded-xl text-xs font-semibold flex items-center gap-2 transition-all ${
                activeTab === 'scripts'
                  ? 'bg-cyan-500/15 text-cyan-300 border border-cyan-500/40 shadow-sm shadow-cyan-500/20'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
              }`}
            >
              <FileText className="w-4 h-4" />
              <span>Topics & Scripts</span>
            </button>

            <button
              onClick={() => setActiveTab('studio')}
              className={`px-3.5 py-2 rounded-xl text-xs font-semibold flex items-center gap-2 transition-all ${
                activeTab === 'studio'
                  ? 'bg-cyan-500/15 text-cyan-300 border border-cyan-500/40 shadow-sm shadow-cyan-500/20'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
              }`}
            >
              <UserCheck className="w-4 h-4" />
              <span>Host Character Studio</span>
            </button>

            <button
              onClick={() => setActiveTab('youtube')}
              className={`px-3.5 py-2 rounded-xl text-xs font-semibold flex items-center gap-2 transition-all ${
                activeTab === 'youtube'
                  ? 'bg-cyan-500/15 text-cyan-300 border border-cyan-500/40 shadow-sm shadow-cyan-500/20'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
              }`}
            >
              <YouTubeIcon className="w-4 h-4" />
              <span>YouTube & Audit</span>
            </button>

            <button
              onClick={() => setActiveTab('monetisation')}
              className={`px-3.5 py-2 rounded-xl text-xs font-semibold flex items-center gap-2 transition-all ${
                activeTab === 'monetisation'
                  ? 'bg-cyan-500/15 text-cyan-300 border border-cyan-500/40 shadow-sm shadow-cyan-500/20'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
              }`}
            >
              <DollarSign className="w-4 h-4" />
              <span>Monetisation Readiness</span>
            </button>
          </nav>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setIsSettingsOpen(true)}
              className="glass-panel p-2 hover:bg-slate-800 text-slate-300 border-slate-700 rounded-xl"
              title="Preferences & System Settings"
            >
              <Settings className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Tab Content Display */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            <MonthlyTracker progress={stats?.monthly_progress} />
            <PipelineOverview
              counts={stats?.pipeline_counts}
              onDiscover={handleDiscoverTopics}
              onRunCycle={handleRunCycle}
              isLoading={isLoading}
            />
            <VideoLibrary videos={videos.slice(0, 3)} onRefresh={loadData} />
          </div>
        )}

        {activeTab === 'videos' && (
          <VideoLibrary videos={videos} onRefresh={loadData} />
        )}

        {activeTab === 'scripts' && (
          <TopicScriptManager
            topics={topics}
            scripts={scripts}
            onGenerateScript={handleGenerateScript}
            onProduceVideo={handleProduceVideo}
            isLoading={isLoading}
          />
        )}

        {activeTab === 'studio' && (
          <CharacterStudio />
        )}

        {activeTab === 'youtube' && (
          <YouTubeManager onRefresh={loadData} />
        )}

        {activeTab === 'monetisation' && (
          <MonetisationView />
        )}

      </main>

      {/* Settings Modal */}
      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        logs={stats?.recent_logs ?? []}
      />
    </div>
  );
};

export default App;
