import React, { useState, useEffect } from 'react';
import {
  DollarSign,
  TrendingUp,
  Users,
  Clock,
  Film,
  ShieldCheck,
  AlertCircle,
  HelpCircle,
  ExternalLink
} from 'lucide-react';
import { MonetisationData } from '../types';
import { api } from '../api';

export const MonetisationView: React.FC = () => {
  const [monetisation, setMonetisation] = useState<MonetisationData | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchMonetisation = async () => {
      try {
        const data = await api.getMonetisation();
        setMonetisation(data);
      } catch (e) {
        console.error(e);
      } finally {
        setIsLoading(false);
      }
    };
    fetchMonetisation();
  }, []);

  if (isLoading || !monetisation) {
    return (
      <div className="glass-panel p-12 text-center text-slate-400 font-mono text-xs">
        Loading YouTube Partner Program (YPP) telemetry...
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="font-heading text-lg font-bold text-slate-100 flex items-center gap-2">
          <DollarSign className="w-5 h-5 text-emerald-400" />
          <span>YouTube Partner Program (YPP) Monetisation Readiness</span>
        </h2>
        <p className="text-xs text-slate-400 mt-0.5">
          Real telemetry tracking against official YouTube monetisation thresholds. No fabricated figures or guarantees.
        </p>
      </div>

      {/* Progress Metric Gauges */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        
        {/* Metric 1: Subscribers */}
        <div className="glass-panel p-5 rounded-xl space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400 font-mono flex items-center gap-1.5">
              <Users className="w-4 h-4 text-cyan-400" />
              Subscribers
            </span>
            <span className="font-mono text-xs font-bold text-cyan-300">
              {monetisation.subscribers_progress_pct}%
            </span>
          </div>

          <div>
            <div className="text-2xl font-bold font-mono text-slate-100">
              {monetisation.subscriber_count.toLocaleString()}
            </div>
            <div className="text-[11px] text-slate-500 font-mono">
              of {monetisation.subscribers_required.toLocaleString()} required for YPP
            </div>
          </div>

          <div className="w-full h-2 bg-slate-950 rounded-full overflow-hidden border border-slate-800">
            <div
              className="h-full bg-gradient-to-r from-cyan-500 to-sky-400 rounded-full transition-all duration-500"
              style={{ width: `${Math.max(2, monetisation.subscribers_progress_pct)}%` }}
            />
          </div>
        </div>

        {/* Metric 2: Public Watch Hours (Long-form) */}
        <div className="glass-panel p-5 rounded-xl space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400 font-mono flex items-center gap-1.5">
              <Clock className="w-4 h-4 text-amber-400" />
              Public Watch Hours
            </span>
            <span className="font-mono text-xs font-bold text-amber-300">
              {monetisation.watch_hours_progress_pct}%
            </span>
          </div>

          <div>
            <div className="text-2xl font-bold font-mono text-slate-100">
              {monetisation.watch_hours.toLocaleString()} hrs
            </div>
            <div className="text-[11px] text-slate-500 font-mono">
              of {monetisation.watch_hours_required.toLocaleString()} public hours required
            </div>
          </div>

          <div className="w-full h-2 bg-slate-950 rounded-full overflow-hidden border border-slate-800">
            <div
              className="h-full bg-gradient-to-r from-amber-500 to-yellow-400 rounded-full transition-all duration-500"
              style={{ width: `${Math.max(2, monetisation.watch_hours_progress_pct)}%` }}
            />
          </div>
        </div>

        {/* Metric 3: Shorts Views (90 Days) */}
        <div className="glass-panel p-5 rounded-xl space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400 font-mono flex items-center gap-1.5">
              <Film className="w-4 h-4 text-violet-400" />
              Shorts Views (90 Days)
            </span>
            <span className="font-mono text-xs font-bold text-violet-300">
              {monetisation.shorts_views_progress_pct}%
            </span>
          </div>

          <div>
            <div className="text-2xl font-bold font-mono text-slate-100">
              {monetisation.shorts_views_90d.toLocaleString()}
            </div>
            <div className="text-[11px] text-slate-500 font-mono">
              of 10,000,000 public Shorts views required
            </div>
          </div>

          <div className="w-full h-2 bg-slate-950 rounded-full overflow-hidden border border-slate-800">
            <div
              className="h-full bg-gradient-to-r from-violet-500 to-purple-400 rounded-full transition-all duration-500"
              style={{ width: `${Math.max(2, monetisation.shorts_views_progress_pct)}%` }}
            />
          </div>
        </div>

      </div>

      {/* Educational Clarification & Policy Checklist */}
      <div className="glass-panel p-5 rounded-xl space-y-4">
        <h4 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
          <HelpCircle className="w-4 h-4 text-cyan-400" />
          <span>YouTube Monetisation Rules & Transparency Guidance</span>
        </h4>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs text-slate-300 leading-relaxed">
          {monetisation.educational_notes.map((note, idx) => (
            <div key={idx} className="p-3 rounded-lg bg-slate-950/60 border border-slate-800/80 flex items-start gap-2.5">
              <span className="font-mono text-cyan-400 font-bold">{idx + 1}.</span>
              <span>{note}</span>
            </div>
          ))}
        </div>

        <div className="pt-3 border-t border-slate-800/80 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs text-slate-400">
          <span>Official YouTube Partner Program guidelines apply. Zero banking credentials stored.</span>
          <a
            href="https://support.google.com/youtube/answer/72851"
            target="_blank"
            rel="noreferrer"
            className="text-cyan-400 hover:text-cyan-300 flex items-center gap-1 font-mono font-medium"
          >
            <span>Google YPP Policies</span>
            <ExternalLink className="w-3 h-3" />
          </a>
        </div>
      </div>
    </div>
  );
};
