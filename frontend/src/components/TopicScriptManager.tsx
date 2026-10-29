import React, { useState } from 'react';
import {
  Compass,
  FileText,
  CheckCircle,
  AlertCircle,
  Sparkles,
  ArrowRight,
  ExternalLink,
  Layers,
  Clock
} from 'lucide-react';
import { TopicItem, ScriptItem } from '../types';

interface TopicScriptManagerProps {
  topics: TopicItem[];
  scripts: ScriptItem[];
  onGenerateScript: (topicId: string) => void;
  onProduceVideo: (scriptId: string) => void;
  isLoading: boolean;
}

export const TopicScriptManager: React.FC<TopicScriptManagerProps> = ({
  topics,
  scripts,
  onGenerateScript,
  onProduceVideo,
  isLoading
}) => {
  const [activeTab, setActiveTab] = useState<'topics' | 'scripts'>('topics');
  const [selectedScript, setSelectedScript] = useState<ScriptItem | null>(null);

  return (
    <div className="space-y-4">
      {/* Tab Switcher */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center gap-3">
          <button
            onClick={() => setActiveTab('topics')}
            className={`px-4 py-2 text-xs font-semibold rounded-lg transition-all flex items-center gap-2 ${
              activeTab === 'topics'
                ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm shadow-cyan-500/20'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Compass className="w-4 h-4" />
            <span>Discovered Topics ({topics.length})</span>
          </button>

          <button
            onClick={() => setActiveTab('scripts')}
            className={`px-4 py-2 text-xs font-semibold rounded-lg transition-all flex items-center gap-2 ${
              activeTab === 'scripts'
                ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm shadow-cyan-500/20'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <FileText className="w-4 h-4" />
            <span>Episode Scripts ({scripts.length})</span>
          </button>
        </div>

        <div className="text-xs text-slate-400 font-mono hidden md:block">
          Deduplicated • Fact-Checked • Zero Superstition
        </div>
      </div>

      {/* Tab 1: Topics */}
      {activeTab === 'topics' && (
        <div className="space-y-3">
          {topics.length === 0 ? (
            <div className="glass-panel p-8 text-center text-slate-400 text-sm">
              No topics discovered yet. Click 'Discover Topics' in the pipeline above.
            </div>
          ) : (
            topics.map((t) => (
              <div
                key={t.id}
                className="glass-panel p-4 rounded-xl flex flex-col md:flex-row md:items-center justify-between gap-4 hover:border-slate-700 transition-all"
              >
                <div className="space-y-1.5 flex-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="badge-tag bg-slate-900 text-slate-300 border border-slate-700 text-[10px]">
                      {t.category}
                    </span>
                    <span className="badge-tag bg-cyan-950 text-cyan-300 border border-cyan-500/30 text-[10px]">
                      {t.format.toUpperCase()}
                    </span>
                    <span className="badge-tag bg-emerald-950 text-emerald-300 border border-emerald-500/30 text-[10px] flex items-center gap-1">
                      <CheckCircle className="w-2.5 h-2.5" />
                      Fact: {t.fact_confidence}%
                    </span>
                    <span className="badge-tag bg-amber-950 text-amber-300 border border-amber-500/30 text-[10px]">
                      Originality: {t.originality_score}%
                    </span>
                  </div>

                  <h3 className="font-malayalam font-bold text-sm text-slate-100">
                    {t.mal_title}
                  </h3>
                  <p className="text-xs text-slate-400 font-mono">
                    {t.title}
                  </p>
                  
                  {t.core_question && (
                    <p className="text-xs text-slate-500 italic">
                      Core Question: {t.core_question}
                    </p>
                  )}
                </div>

                <div className="flex items-center gap-3">
                  {t.status === 'discovered' ? (
                    <button
                      onClick={() => onGenerateScript(t.id)}
                      disabled={isLoading}
                      className="px-3.5 py-2 bg-cyan-600 hover:bg-cyan-500 text-white font-semibold text-xs rounded-lg flex items-center gap-1.5 shadow-md shadow-cyan-900/30"
                    >
                      <Sparkles className="w-3.5 h-3.5" />
                      <span>Author Script</span>
                    </button>
                  ) : (
                    <span className="badge-tag bg-slate-900 text-slate-400 border border-slate-800 text-[11px]">
                      Status: {t.status}
                    </span>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* Tab 2: Scripts */}
      {activeTab === 'scripts' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <div className="space-y-3">
            {scripts.map((s) => (
              <div
                key={s.id}
                onClick={() => setSelectedScript(s)}
                className={`glass-panel p-4 rounded-xl cursor-pointer transition-all border ${
                  selectedScript?.id === s.id ? 'border-cyan-400 bg-slate-900/90 shadow-md shadow-cyan-500/10' : 'border-slate-800 hover:border-slate-700'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="badge-tag bg-slate-900 text-cyan-300 border border-slate-700 text-[10px]">
                    {s.format.toUpperCase()} • ~{s.estimated_duration_sec}s
                  </span>
                  <span className="text-[11px] font-mono text-slate-400">
                    {s.word_count} Words
                  </span>
                </div>

                <h4 className="font-malayalam font-bold text-sm text-slate-100 line-clamp-2 mb-1.5">
                  {s.mal_title || s.topic_title}
                </h4>

                <p className="font-malayalam text-xs text-slate-400 line-clamp-2">
                  {s.mal_hook}
                </p>

                <div className="mt-3 pt-2 border-t border-slate-800 flex items-center justify-between text-xs">
                  <span className="font-mono text-[11px] text-slate-500">
                    Engine: {s.model_used}
                  </span>
                  <span className="text-cyan-400 font-medium flex items-center gap-1">
                    View Script & Cues <ArrowRight className="w-3 h-3" />
                  </span>
                </div>
              </div>
            ))}
          </div>

          {/* Script Detail Inspector */}
          <div className="glass-panel p-5 rounded-xl flex flex-col justify-between">
            {selectedScript ? (
              <div className="space-y-4">
                <div className="flex items-start justify-between gap-3 border-b border-slate-800 pb-3">
                  <div>
                    <h3 className="font-malayalam font-bold text-base text-slate-100">
                      {selectedScript.mal_title || selectedScript.topic_title}
                    </h3>
                    <div className="text-xs text-slate-400 font-mono mt-0.5">
                      Script ID: {selectedScript.id} • Model: {selectedScript.model_used}
                    </div>
                  </div>

                  <button
                    onClick={() => onProduceVideo(selectedScript.id)}
                    disabled={isLoading}
                    className="px-4 py-2 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 text-white font-bold text-xs rounded-lg flex items-center gap-1.5 shadow-md shadow-emerald-900/30 whitespace-nowrap"
                  >
                    <span>Produce Video Now</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>

                {/* Script Sections */}
                <div className="space-y-3 font-malayalam text-xs leading-relaxed max-h-80 overflow-y-auto pr-2">
                  <div className="p-3 rounded-lg bg-amber-950/30 border border-amber-500/20">
                    <div className="font-sans font-bold text-[11px] text-amber-300 mb-1">
                      1. Opening Hook (കൗതുകമുണർത്തുന്ന തുടക്കം):
                    </div>
                    <p className="text-slate-200">{selectedScript.mal_hook}</p>
                  </div>

                  <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800">
                    <div className="font-sans font-bold text-[11px] text-cyan-300 mb-1">
                      2. Scientific Core Narrative (ശാസ്ത്രീയ വിവരണം):
                    </div>
                    <p className="text-slate-200">{selectedScript.mal_content}</p>
                  </div>

                  <div className="p-3 rounded-lg bg-indigo-950/30 border border-indigo-500/20">
                    <div className="font-sans font-bold text-[11px] text-indigo-300 mb-1">
                      3. Informative Conclusion & CTA (ഉപസംഹാരം):
                    </div>
                    <p className="text-slate-200">{selectedScript.mal_conclusion}</p>
                  </div>
                </div>

                {/* Scene Cues */}
                {selectedScript.scenes && selectedScript.scenes.length > 0 && (
                  <div>
                    <h4 className="text-xs font-semibold text-slate-300 mb-2 flex items-center gap-1.5">
                      <Layers className="w-3.5 h-3.5 text-cyan-400" />
                      <span>3D Scene & jobelessboy Visual Cues ({selectedScript.scenes.length} Scenes):</span>
                    </h4>
                    <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
                      {selectedScript.scenes.map((sc, i) => (
                        <div key={i} className="p-2.5 rounded-lg bg-slate-900/80 border border-slate-800/80 text-[11px]">
                          <div className="flex justify-between font-mono text-cyan-400 mb-1">
                            <span>Scene {sc.scene_number} ({sc.duration_sec}s)</span>
                            <span className="text-amber-400 font-semibold">{sc.character_expression}</span>
                          </div>
                          <div className="text-slate-300">{sc.visual_description}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="h-full flex items-center justify-center text-slate-500 text-xs italic">
                Select a script from the list to view its narration, narration text, and 3D scene cues.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
