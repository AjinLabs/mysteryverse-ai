import React from 'react';
import {
  Compass,
  FileText,
  UserCheck,
  Mic,
  Video,
  ShieldCheck,
  UploadCloud,
  ChevronRight,
  ArrowRight
} from 'lucide-react';
import { PipelineCounts } from '../types';

interface PipelineOverviewProps {
  counts?: PipelineCounts;
  onDiscover: () => void;
  onRunCycle: () => void;
  isLoading: boolean;
}

export const PipelineOverview: React.FC<PipelineOverviewProps> = ({
  counts,
  onDiscover,
  onRunCycle,
  isLoading
}) => {
  const steps = [
    {
      id: 'research',
      title: '1. Research Agent',
      desc: 'Multi-source RSS & fact verify',
      count: counts?.discovered_topics ?? 0,
      badge: 'Topics',
      icon: Compass,
      color: 'text-amber-400',
      border: 'border-amber-500/30'
    },
    {
      id: 'script',
      title: '2. English Scripts',
      desc: 'Scientific storytelling',
      count: counts?.total_scripts ?? 0,
      badge: 'Scripts',
      icon: FileText,
      color: 'text-cyan-400',
      border: 'border-cyan-500/30'
    },
    {
      id: 'character',
      title: '3. jobelessboy 3D',
      desc: 'Host bible & animations',
      count: 6,
      badge: 'Expressions',
      icon: UserCheck,
      color: 'text-indigo-400',
      border: 'border-indigo-500/30'
    },
    {
      id: 'audio',
      title: '4. Voice & SRT',
      desc: 'Broadcast Neural Voice',
      count: counts?.rendering_jobs ?? 0,
      badge: 'Voicing',
      icon: Mic,
      color: 'text-emerald-400',
      border: 'border-emerald-500/30'
    },
    {
      id: 'render',
      title: '5. FFmpeg Composite',
      desc: '1080x1920 & 1920x1080',
      count: counts?.rendering_jobs ?? 0,
      badge: 'Rendering',
      icon: Video,
      color: 'text-violet-400',
      border: 'border-violet-500/30'
    },
    {
      id: 'quality',
      title: '6. Quality Gates',
      desc: 'Originality & file audits',
      count: counts?.ready_for_upload ?? 0,
      badge: 'Approved',
      icon: ShieldCheck,
      color: 'text-emerald-400',
      border: 'border-emerald-500/30'
    },
    {
      id: 'upload',
      title: '7. YouTube Release',
      desc: 'Asia/Kolkata scheduled',
      count: counts?.scheduled_videos ?? 0,
      badge: 'Scheduled',
      icon: UploadCloud,
      color: 'text-sky-400',
      border: 'border-sky-500/30'
    }
  ];

  return (
    <div className="glass-panel p-5">
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-3 mb-5">
        <div>
          <h2 className="font-heading text-lg font-bold text-slate-100 flex items-center gap-2">
            <span>Autonomous Production Pipeline</span>
            <span className="badge-tag bg-cyan-950 text-cyan-300 border border-cyan-500/30 text-[10px]">
              Continuous State Machine
            </span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Every video traverses 7 strict autonomous verification gates before reaching YouTube.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={onDiscover}
            disabled={isLoading}
            className="glass-panel px-3 py-1.5 hover:bg-slate-800 text-xs text-slate-200 border-slate-700 flex items-center gap-1.5 rounded-lg"
          >
            <Compass className="w-3.5 h-3.5 text-amber-400" />
            <span>Discover Topics</span>
          </button>

          <button
            onClick={onRunCycle}
            disabled={isLoading}
            className="px-3.5 py-1.5 bg-gradient-to-r from-cyan-600 to-sky-600 hover:from-cyan-500 hover:to-sky-500 text-white text-xs font-semibold flex items-center gap-1.5 rounded-lg shadow-md shadow-cyan-900/40"
          >
            <span>Run Pipeline</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Stepper Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3">
        {steps.map((step, idx) => {
          const Icon = step.icon;
          return (
            <div
              key={step.id}
              className={`bg-slate-900/70 p-3 rounded-xl border ${step.border} flex flex-col justify-between hover:bg-slate-900 transition-all`}
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <div className={`p-1.5 rounded-lg bg-slate-950 ${step.color}`}>
                    <Icon className="w-4 h-4" />
                  </div>
                  <span className="font-mono text-xs font-bold text-slate-200">
                    {step.count}
                  </span>
                </div>

                <div className="text-xs font-semibold text-slate-200 leading-tight">
                  {step.title}
                </div>
                <div className="text-[10px] text-slate-400 mt-1 line-clamp-1">
                  {step.desc}
                </div>
              </div>

              <div className="mt-3 pt-2 border-t border-slate-800/80 flex items-center justify-between text-[10px] text-slate-500 font-mono">
                <span>{step.badge}</span>
                <span className="text-cyan-400">READY</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
