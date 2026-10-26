import React from 'react';
import { Film, Video, Target, Sparkles, DollarSign } from 'lucide-react';
import { MonthlyProgress } from '../types';

interface MonthlyTrackerProps {
  progress?: MonthlyProgress;
}

export const MonthlyTracker: React.FC<MonthlyTrackerProps> = ({ progress }) => {
  const shortsProduced = progress?.shorts_produced ?? 0;
  const shortsTarget = progress?.shorts_target ?? 30;
  const shortsPct = progress?.shorts_pct ?? 0;

  const longsProduced = progress?.longs_produced ?? 0;
  const longsTarget = progress?.longs_target ?? 30;
  const longsPct = progress?.longs_pct ?? 0;

  const totalProduced = progress?.total_produced ?? (shortsProduced + longsProduced);
  const totalTarget = progress?.total_target ?? 60;
  const totalPct = Math.min(100, Math.round((totalProduced / totalTarget) * 100));

  return (
    <div className="glass-panel p-5 relative overflow-hidden">
      {/* Subtle background glow */}
      <div className="absolute -top-12 -right-12 w-48 h-48 rounded-full bg-cyan-500/10 blur-3xl pointer-events-none" />

      <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4 mb-4">
        <div>
          <div className="flex items-center gap-2">
            <Target className="w-5 h-5 text-cyan-400" />
            <h2 className="font-heading text-lg font-bold text-slate-100">
              Monthly Production Cadence
            </h2>
            <span className="badge-tag bg-emerald-950/80 text-emerald-300 border border-emerald-500/30">
              <DollarSign className="w-3 h-3" />
              ₹0 Budget Active
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Targeting 60 high-quality educational videos per month (30 Shorts + 30 Longs). Quality gates strictly enforced.
          </p>
        </div>

        <div className="flex items-center gap-3 bg-slate-900/80 px-4 py-2 rounded-xl border border-slate-800">
          <div className="text-right font-mono">
            <div className="text-xs text-slate-400">Total Output</div>
            <div className="text-sm font-bold text-cyan-400">
              {totalProduced} <span className="text-slate-500">/ {totalTarget} videos</span>
            </div>
          </div>
          <div className="w-10 h-10 rounded-full border-2 border-cyan-500/40 flex items-center justify-center font-bold text-xs text-cyan-300">
            {totalPct}%
          </div>
        </div>
      </div>

      {/* Target Progress Bars */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        
        {/* Shorts Target */}
        <div className="bg-slate-900/60 p-3.5 rounded-xl border border-slate-800/80">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <Film className="w-4 h-4 text-amber-400" />
              <span className="text-xs font-semibold text-slate-200">YouTube Shorts (1080x1920)</span>
            </div>
            <span className="font-mono text-xs font-bold text-amber-400">
              {shortsProduced} / {shortsTarget}
            </span>
          </div>

          <div className="w-full h-2.5 bg-slate-950 rounded-full overflow-hidden p-0.5 border border-slate-800">
            <div
              className="h-full bg-gradient-to-r from-amber-500 to-amber-300 rounded-full transition-all duration-500 shadow-sm shadow-amber-500/50"
              style={{ width: `${Math.max(4, shortsPct)}%` }}
            />
          </div>
          <div className="flex justify-between items-center text-[11px] text-slate-500 mt-1.5 font-mono">
            <span>Fast-paced 30–60s mystery explainers</span>
            <span>{shortsPct}% Completed</span>
          </div>
        </div>

        {/* Long-form Target */}
        <div className="bg-slate-900/60 p-3.5 rounded-xl border border-slate-800/80">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <Video className="w-4 h-4 text-cyan-400" />
              <span className="text-xs font-semibold text-slate-200">Long-Form Deep Dives (1920x1080)</span>
            </div>
            <span className="font-mono text-xs font-bold text-cyan-400">
              {longsProduced} / {longsTarget}
            </span>
          </div>

          <div className="w-full h-2.5 bg-slate-950 rounded-full overflow-hidden p-0.5 border border-slate-800">
            <div
              className="h-full bg-gradient-to-r from-cyan-500 to-indigo-400 rounded-full transition-all duration-500 shadow-sm shadow-cyan-500/50"
              style={{ width: `${Math.max(4, longsPct)}%` }}
            />
          </div>
          <div className="flex justify-between items-center text-[11px] text-slate-500 mt-1.5 font-mono">
            <span>5–10m deeply researched science mysteries</span>
            <span>{longsPct}% Completed</span>
          </div>
        </div>

      </div>
    </div>
  );
};
