import React from 'react';
import {
  Radio,
  Power,
  AlertTriangle,
  Play,
  Pause,
  ExternalLink,
  ShieldCheck,
  HardDrive,
  Cpu,
  Layers
} from 'lucide-react';
import { DashboardStats } from '../types';

interface HeaderProps {
  stats: DashboardStats | null;
  onToggleScheduler: () => void;
  onToggleKillswitch: () => void;
  onRunCycle: () => void;
  isLoading: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  stats,
  onToggleScheduler,
  onToggleKillswitch,
  onRunCycle,
  isLoading
}) => {
  const isKillswitchActive = stats?.system_status.killswitch_active ?? false;
  const isSchedulerActive = stats?.system_status.autonomous_scheduler_active ?? false;
  const isChannelConnected = stats?.channel.is_connected ?? false;

  return (
    <header className="glass-panel border-b border-cyan-500/20 px-6 py-4 sticky top-0 z-50 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        
        {/* Brand & Channel Identity */}
        <div className="flex items-center gap-4">
          <div className="relative">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-cyan-500/20 to-violet-500/20 border border-cyan-400/40 flex items-center justify-center shadow-lg shadow-cyan-500/10">
              <Radio className="w-6 h-6 text-cyan-400 animate-pulse" />
            </div>
            {isSchedulerActive && !isKillswitchActive && (
              <span className="absolute -top-1 -right-1 w-3.5 h-3.5 rounded-full bg-emerald-400 border-2 border-slate-900 pulse-dot" />
            )}
          </div>

          <div>
            <div className="flex items-center gap-2">
              <h1 className="font-heading text-xl font-bold tracking-wider text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-sky-300 to-indigo-300">
                MYSTERYVERSE AI
              </h1>
              <span className="badge-tag bg-cyan-950/80 text-cyan-300 border border-cyan-500/30 text-[10px]">
                Autonomous v1.0
              </span>
            </div>

            <div className="flex items-center gap-2 mt-0.5">
              <a
                href="https://www.youtube.com/@MYSTERYVERSE-MALAYALAM"
                target="_blank"
                rel="noreferrer"
                className="text-xs text-slate-300 hover:text-cyan-300 flex items-center gap-1 font-mono transition-colors"
              >
                <span>@MYSTERYVERSE-MALAYALAM</span>
                <ExternalLink className="w-3 h-3 text-slate-400" />
              </a>

              <span className="text-slate-600">•</span>

              <span className={`text-[11px] font-medium flex items-center gap-1 ${
                isChannelConnected ? 'text-emerald-400' : 'text-amber-400'
              }`}>
                <ShieldCheck className="w-3 h-3" />
                {isChannelConnected ? 'Verified Channel' : 'OAuth Staging'}
              </span>
            </div>
          </div>
        </div>

        {/* Telemetry quick indicators */}
        <div className="hidden xl:flex items-center gap-4 text-xs font-mono">
          <div className="glass-panel px-3 py-1.5 flex items-center gap-2 text-slate-300 border-slate-800">
            <Cpu className="w-3.5 h-3.5 text-cyan-400" />
            <span>FFmpeg: {stats?.system_status.ffmpeg_detected ? 'v7.1 Ready' : 'Pending'}</span>
          </div>

          <div className="glass-panel px-3 py-1.5 flex items-center gap-2 text-slate-300 border-slate-800">
            <Layers className="w-3.5 h-3.5 text-violet-400" />
            <span>Blender: {stats?.system_status.blender_detected ? '3D Active' : 'Procedural 3D'}</span>
          </div>

          <div className="glass-panel px-3 py-1.5 flex items-center gap-2 text-slate-300 border-slate-800">
            <HardDrive className="w-3.5 h-3.5 text-emerald-400" />
            <span>Disk: {stats?.system_status.disk_free_gb ?? 0} GB Free</span>
          </div>
        </div>

        {/* Master Controls & Emergency Switches */}
        <div className="flex items-center gap-3">
          {/* Quick trigger cycle */}
          <button
            onClick={onRunCycle}
            disabled={isLoading || isKillswitchActive}
            className="glass-panel px-3.5 py-2 hover:bg-cyan-950/40 border-cyan-500/40 text-cyan-300 hover:text-cyan-100 text-xs font-semibold flex items-center gap-2 rounded-lg"
            title="Produce next video in autonomous queue immediately"
          >
            <Play className="w-3.5 h-3.5 fill-cyan-400" />
            <span>Run Cycle Now</span>
          </button>

          {/* Autonomous Scheduler Master Switch */}
          <button
            onClick={onToggleScheduler}
            disabled={isKillswitchActive}
            className={`px-3.5 py-2 text-xs font-semibold rounded-lg flex items-center gap-2 border transition-all ${
              isSchedulerActive
                ? 'bg-emerald-500/20 border-emerald-500/50 text-emerald-300 hover:bg-emerald-500/30'
                : 'bg-slate-800/80 border-slate-700 text-slate-400 hover:bg-slate-700/80'
            }`}
          >
            {isSchedulerActive ? (
              <>
                <Pause className="w-3.5 h-3.5 text-emerald-400" />
                <span>Auto: RUNNING</span>
              </>
            ) : (
              <>
                <Play className="w-3.5 h-3.5 text-slate-400" />
                <span>Auto: PAUSED</span>
              </>
            )}
          </button>

          {/* Emergency Kill Switch */}
          <button
            onClick={onToggleKillswitch}
            className={`px-3.5 py-2 text-xs font-bold rounded-lg flex items-center gap-2 transition-all ${
              isKillswitchActive
                ? 'bg-rose-600 text-white glow-box-red animate-pulse'
                : 'bg-rose-950/40 hover:bg-rose-900/60 border border-rose-500/40 text-rose-300'
            }`}
            title="Instantly abort all rendering, scheduling, and YouTube uploads"
          >
            <AlertTriangle className="w-3.5 h-3.5" />
            <span>{isKillswitchActive ? 'KILLSWITCH ACTIVE' : 'KILL SWITCH'}</span>
          </button>
        </div>

      </div>
    </header>
  );
};
