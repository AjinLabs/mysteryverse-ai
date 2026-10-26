import React, { useState, useEffect } from 'react';
import {
  ExternalLink,
  Key,
  RefreshCw,
  Sliders
} from 'lucide-react';
import { YouTubeIcon } from './YouTubeIcon';
import { ChannelAuditData } from '../types';
import { api } from '../api';

interface YouTubeManagerProps {
  onRefresh: () => void;
}

export const YouTubeManager: React.FC<YouTubeManagerProps> = ({ onRefresh }) => {
  const [auditData, setAuditData] = useState<ChannelAuditData | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [demoEnabled, setDemoEnabled] = useState<boolean>(true);

  const fetchAudit = async () => {
    try {
      setIsLoading(true);
      const data = await api.getChannelAudit();
      setAuditData(data);
    } catch (e) {
      console.error('Failed to fetch audit data:', e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchAudit();
  }, []);

  const handleToggleDemo = async () => {
    try {
      setIsLoading(true);
      const newMode = !demoEnabled;
      await api.toggleDemoConnect(newMode);
      setDemoEnabled(newMode);
      await fetchAudit();
      onRefresh();
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-3">
        <div>
          <h2 className="font-heading text-lg font-bold text-slate-100 flex items-center gap-2">
            <YouTubeIcon className="w-5 h-5 text-rose-500" />
            <span>YouTube Channel Operations & OAuth 2.0</span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Official Google Cloud OAuth 2.0 integration for @MYSTERYVERSE-MALAYALAM. Minimum scopes, protected tokens.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleToggleDemo}
            disabled={isLoading}
            className={`px-3.5 py-1.5 text-xs font-semibold rounded-lg border transition-all ${
              demoEnabled
                ? 'bg-cyan-500/20 border-cyan-500/40 text-cyan-300'
                : 'bg-slate-850 border-slate-700 text-slate-400'
            }`}
          >
            {demoEnabled ? 'Demo Channel: CONNECTED' : 'Enable Demo Mode'}
          </button>

          <button
            onClick={fetchAudit}
            disabled={isLoading}
            className="glass-panel px-3 py-1.5 text-xs text-slate-300 hover:bg-slate-800 rounded-lg flex items-center gap-1"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
            <span>Audit</span>
          </button>
        </div>
      </div>

      {/* Target Channel Profile Card */}
      <div className="glass-panel p-5 rounded-2xl border-cyan-500/30">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-rose-500/20 to-indigo-500/20 border border-rose-500/40 flex items-center justify-center">
              <YouTubeIcon className="w-8 h-8 text-rose-400" />
            </div>

            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-heading text-base font-bold text-slate-100">
                  MYSTERY VERSE MALAYALAM
                </h3>
                <span className="badge-tag bg-emerald-950/80 text-emerald-300 border border-emerald-500/40 text-[10px]">
                  Target Confirmed
                </span>
              </div>

              <div className="flex items-center gap-3 text-xs text-slate-400 font-mono mt-1">
                <a
                  href="https://www.youtube.com/@MYSTERYVERSE-MALAYALAM"
                  target="_blank"
                  rel="noreferrer"
                  className="text-cyan-400 hover:underline flex items-center gap-1"
                >
                  <span>@MYSTERYVERSE-MALAYALAM</span>
                  <ExternalLink className="w-3 h-3" />
                </a>
                <span>•</span>
                <span>Language: Malayalam (മലയാളം)</span>
                <span>•</span>
                <span>Category: Education (27)</span>
              </div>
            </div>
          </div>

          <div className="text-right">
            <div className="text-xs text-slate-400 font-mono">Publishing Schedule</div>
            <div className="text-xs font-bold text-amber-400 font-mono mt-0.5">
              18:30 IST (Shorts) • 20:00 IST (Longs)
            </div>
          </div>
        </div>
      </div>

      {/* Two columns: OAuth Setup Walkthrough & Channel Configuration Audit */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Google OAuth Setup Guide */}
        <div className="glass-panel p-5 rounded-xl space-y-4">
          <h4 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
            <Key className="w-4 h-4 text-cyan-400" />
            <span>Google Cloud OAuth 2.0 Credentials Setup</span>
          </h4>

          <p className="text-xs text-slate-300 leading-relaxed">
            The owner never shares their password with the application. Complete this one-time setup:
          </p>

          <ol className="space-y-2.5 text-xs text-slate-300 list-decimal list-inside leading-relaxed font-mono">
            <li className="p-2.5 rounded-lg bg-slate-950/60 border border-slate-800">
              <span className="text-cyan-300 font-semibold font-sans">Step 1:</span> Open Google Cloud Console and create project <code className="text-amber-300 font-mono">Mysteryverse-Media</code>.
            </li>
            <li className="p-2.5 rounded-lg bg-slate-950/60 border border-slate-800">
              <span className="text-cyan-300 font-semibold font-sans">Step 2:</span> Enable <strong>YouTube Data API v3</strong> in the APIs & Services library.
            </li>
            <li className="p-2.5 rounded-lg bg-slate-950/60 border border-slate-800">
              <span className="text-cyan-300 font-semibold font-sans">Step 3:</span> Configure OAuth Consent Screen and add redirect URI: <code className="text-emerald-400">http://localhost:8000/api/youtube/oauth2callback</code>
            </li>
            <li className="p-2.5 rounded-lg bg-slate-950/60 border border-slate-800">
              <span className="text-cyan-300 font-semibold font-sans">Step 4:</span> Download OAuth client credentials JSON as <code className="text-amber-300 font-mono">client_secrets.json</code> and place in <code className="text-slate-400 font-mono">backend/data/</code>.
            </li>
          </ol>
        </div>

        {/* Channel Configuration Audit Items */}
        <div className="glass-panel p-5 rounded-xl space-y-4">
          <h4 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
            <Sliders className="w-4 h-4 text-amber-400" />
            <span>Channel Configuration Audit & Manual Actions</span>
          </h4>

          <p className="text-xs text-slate-400 leading-relaxed">
            Settings YouTube protects from third-party APIs must be verified directly by the owner in YouTube Studio:
          </p>

          <div className="space-y-3">
            {auditData?.manual_action_items.map((item, idx) => (
              <div key={idx} className="p-3 rounded-lg bg-slate-950/70 border border-slate-800 text-xs space-y-1">
                <div className="flex items-center justify-between font-bold text-slate-200">
                  <span>{item.setting}</span>
                  <span className="text-[10px] text-amber-400 font-mono bg-amber-950/60 px-2 py-0.5 rounded border border-amber-500/30">
                    {item.status}
                  </span>
                </div>
                <div className="text-slate-400 text-[11px]">{item.reason}</div>
                <div className="text-cyan-400 text-[11px] font-mono mt-1 pt-1 border-t border-slate-900">
                  👉 {item.instruction}
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>
    </div>
  );
};
