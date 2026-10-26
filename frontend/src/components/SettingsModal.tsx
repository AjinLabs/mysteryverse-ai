import React, { useState, useEffect } from 'react';
import {
  Settings,
  Key,
  Volume2,
  Terminal,
  ShieldCheck,
  Check,
  X
} from 'lucide-react';
import { api } from '../api';
import { SystemLog } from '../types';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  logs: SystemLog[];
}

export const SettingsModal: React.FC<SettingsModalProps> = ({ isOpen, onClose, logs }) => {
  const [geminiKey, setGeminiKey] = useState<string>('');
  const [selectedVoice, setSelectedVoice] = useState<string>('ml-IN-MidhunNeural');
  const [autoPublish, setAutoPublish] = useState<boolean>(true);
  const [savedSuccess, setSavedSuccess] = useState<boolean>(false);

  useEffect(() => {
    if (isOpen) {
      api.getSettings().then((res) => {
        if (res.default_voice) setSelectedVoice(res.default_voice);
        setAutoPublish(res.auto_publish_enabled ?? true);
      }).catch(console.error);
    }
  }, [isOpen]);

  const handleSave = async () => {
    try {
      await api.updateSettings({
        gemini_api_key: geminiKey.trim() || undefined,
        default_voice: selectedVoice,
        auto_publish_enabled: autoPublish
      });
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 2500);
    } catch (e) {
      console.error(e);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4">
      <div className="glass-panel w-full max-w-2xl max-h-[90vh] overflow-y-auto rounded-2xl border-cyan-500/40 p-6 relative space-y-6">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <h3 className="font-heading font-bold text-lg text-slate-100 flex items-center gap-2">
            <Settings className="w-5 h-5 text-cyan-400" />
            <span>Autonomous Preferences & System Settings</span>
          </h3>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Setting 1: Gemini Free-Tier API Key */}
        <div className="space-y-2">
          <label className="text-xs font-semibold text-slate-200 flex items-center gap-1.5">
            <Key className="w-4 h-4 text-amber-400" />
            <span>Google Gemini API Key (Free Tier Optional):</span>
          </label>
          <input
            type="password"
            placeholder="Paste Gemini free tier API key (optional - local engine active)"
            value={geminiKey}
            onChange={(e) => setGeminiKey(e.target.value)}
            className="w-full px-3.5 py-2.5 rounded-lg bg-slate-950 border border-slate-800 focus:border-cyan-500 text-xs text-slate-100 outline-none font-mono"
          />
          <p className="text-[11px] text-slate-500">
            If left blank, MYSTERYVERSE AI automatically uses the high-speed local Malayalam neural template engine at ₹0 cost.
          </p>
        </div>

        {/* Setting 2: Malayalam Voice Profile */}
        <div className="space-y-2">
          <label className="text-xs font-semibold text-slate-200 flex items-center gap-1.5">
            <Volume2 className="w-4 h-4 text-cyan-400" />
            <span>Default Malayalam Neural Voice:</span>
          </label>
          <div className="grid grid-cols-2 gap-3">
            <div
              onClick={() => setSelectedVoice('ml-IN-MidhunNeural')}
              className={`p-3 rounded-xl border cursor-pointer text-xs transition-all ${
                selectedVoice === 'ml-IN-MidhunNeural'
                  ? 'border-cyan-500 bg-cyan-950/40 text-cyan-200'
                  : 'border-slate-800 bg-slate-950/60 text-slate-400 hover:border-slate-700'
              }`}
            >
              <div className="font-bold text-slate-100">Midhun (Male)</div>
              <div className="text-[11px] text-slate-400 mt-0.5">Energetic, deep mystery explainer</div>
            </div>

            <div
              onClick={() => setSelectedVoice('ml-IN-SobhanaNeural')}
              className={`p-3 rounded-xl border cursor-pointer text-xs transition-all ${
                selectedVoice === 'ml-IN-SobhanaNeural'
                  ? 'border-cyan-500 bg-cyan-950/40 text-cyan-200'
                  : 'border-slate-800 bg-slate-950/60 text-slate-400 hover:border-slate-700'
              }`}
            >
              <div className="font-bold text-slate-100">Sobhana (Female)</div>
              <div className="text-[11px] text-slate-400 mt-0.5">Articulate, warm educational narrator</div>
            </div>
          </div>
        </div>

        {/* Setting 3: Auto-Publish Policy */}
        <div className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800 flex items-center justify-between">
          <div>
            <div className="text-xs font-bold text-slate-200">Autonomous YouTube Scheduled Uploads</div>
            <div className="text-[11px] text-slate-500">
              When enabled, videos passing all quality gates are automatically scheduled for 18:30 IST / 20:00 IST.
            </div>
          </div>
          <button
            onClick={() => setAutoPublish(!autoPublish)}
            className={`w-12 h-6 rounded-full transition-colors relative p-1 ${
              autoPublish ? 'bg-cyan-500' : 'bg-slate-800'
            }`}
          >
            <div
              className={`w-4 h-4 rounded-full bg-slate-950 transition-transform ${
                autoPublish ? 'translate-x-6' : 'translate-x-0'
              }`}
            />
          </button>
        </div>

        {/* Live System Event Logs Terminal */}
        <div className="space-y-2">
          <label className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
            <Terminal className="w-4 h-4 text-emerald-400" />
            <span>Autonomous System Audit Trail & Logs:</span>
          </label>
          <div className="p-3 bg-slate-950 rounded-xl border border-slate-800 max-h-44 overflow-y-auto font-mono text-[11px] text-slate-300 space-y-1">
            {logs.length === 0 ? (
              <div className="text-slate-600">No events logged yet.</div>
            ) : (
              logs.map((log) => (
                <div key={log.id} className="flex items-start gap-2">
                  <span className="text-slate-600">[{log.created_at.slice(11, 19)}]</span>
                  <span className={log.level === 'ERROR' ? 'text-rose-400' : log.level === 'WARNING' ? 'text-amber-400' : 'text-cyan-400'}>
                    [{log.source}]
                  </span>
                  <span className="text-slate-300">{log.message}</span>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-800">
          {savedSuccess && (
            <span className="text-xs text-emerald-400 font-mono flex items-center gap-1">
              <Check className="w-3.5 h-3.5" />
              Settings saved successfully!
            </span>
          )}
          <button
            onClick={handleSave}
            className="px-5 py-2 bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-xs rounded-lg shadow-md shadow-cyan-900/30"
          >
            Save Configuration
          </button>
        </div>
      </div>
    </div>
  );
};
