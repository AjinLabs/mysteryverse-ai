import React, { useState } from 'react';
import {
  User,
  Sparkles,
  Camera,
  Layers,
  Palette,
  Volume2,
  Smile,
  ShieldCheck,
  CheckCircle2
} from 'lucide-react';

export const CharacterStudio: React.FC = () => {
  const [selectedExpression, setSelectedExpression] = useState<string>('explanation');

  const expressions = [
    { id: 'explanation', name: 'Explanation (വിവരണം)', desc: 'Direct center gaze, friendly articulate presentation' },
    { id: 'waving', name: 'Friendly Wave (കൈവീശൽ)', desc: 'Warm animated opening wave welcoming viewers to the video' },
    { id: 'talking_wide', name: 'Active Speaking (സംസാരം)', desc: 'Dynamic mouth movement and expressive articulation of facts' },
    { id: 'curiosity', name: 'Curiosity (കൗതുകം)', desc: 'One eyebrow raised, head tilted observing a cosmic anomaly' },
    { id: 'surprise', name: 'Surprise (വിസ്മയം)', desc: 'Wide eyes, gasping at an unexpected scientific discovery' },
    { id: 'excitement', name: 'Excitement (ആവേശം)', desc: 'Enthusiastic broad smile presenting breakthroughs' },
    { id: 'welcome', name: 'Call to Action (സബ്സ്ക്രൈബ്)', desc: 'Enthusiastic pointing to subscribe and join the mystery journey' },
    { id: 'caution', name: 'Caution (ജാഗ്രത)', desc: 'Serious furrowed brow warning against pseudoscience' },
    { id: 'humour', name: 'Humour (ഫലിതം)', desc: 'Wry asymmetrical smirk with playful amused nod' }
  ];

  return (
    <div className="space-y-5">
      <div>
        <h2 className="font-heading text-lg font-bold text-slate-100 flex items-center gap-2">
          <span>Official Channel Host & 3D Studio</span>
          <span className="badge-tag bg-cyan-950 text-cyan-300 border border-cyan-500/30 text-[10px]">
            Original Recurring Identity
          </span>
        </h2>
        <p className="text-xs text-slate-400 mt-0.5">
          Meet jobelessboy (ജോബ്‌ലെസ് ബോയ്) — the official animated host representing @MYSTERYVERSE-MALAYALAM.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left: Interactive 3D/Sprite Character Visualizer */}
        <div className="glass-panel p-6 rounded-2xl flex flex-col items-center justify-between text-center border-cyan-500/30">
          <div className="relative w-64 h-64 mx-auto mb-4 flex items-center justify-center">
            {/* Ambient cyber glow ring */}
            <div className="absolute inset-0 rounded-full bg-cyan-500/20 blur-2xl animate-pulse pointer-events-none" />
            
            <img
              src={`/static/character/jobelessboy_${selectedExpression}.png`}
              alt={`jobelessboy - ${selectedExpression}`}
              className="w-full h-full object-contain relative z-10 drop-shadow-[0_15px_25px_rgba(6,182,212,0.3)] transition-all duration-300"
            />
          </div>

          <div>
            <h3 className="font-heading text-xl font-bold text-cyan-300">
              jobelessboy
            </h3>
            <p className="font-malayalam text-xs text-slate-400 mt-1">
              ജോബ്‌ലെസ് ബോയ് (Cosmic Mystery Sleuth)
            </p>
            <div className="badge-tag bg-slate-900 text-slate-300 border border-slate-700 text-[11px] mt-2">
              Expression: <span className="text-cyan-400 font-bold ml-1">{selectedExpression.toUpperCase()}</span>
            </div>
          </div>

          {/* Quick Expression Switcher Buttons */}
          <div className="grid grid-cols-3 gap-2 mt-5 w-full">
            {expressions.map((e) => (
              <button
                key={e.id}
                onClick={() => setSelectedExpression(e.id)}
                className={`py-1.5 px-2 rounded-lg text-[10px] font-semibold transition-all border ${
                  selectedExpression === e.id
                    ? 'bg-cyan-500 text-slate-950 border-cyan-400 shadow-md shadow-cyan-500/30'
                    : 'bg-slate-900/80 text-slate-400 border-slate-800 hover:text-slate-200'
                }`}
              >
                {e.id}
              </button>
            ))}
          </div>
        </div>

        {/* Right 2 cols: Character Bible Specifications */}
        <div className="lg:col-span-2 space-y-4">
          
          {/* Identity & Visual Design Guidelines */}
          <div className="glass-panel p-5 rounded-xl space-y-3">
            <h4 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
              <User className="w-4 h-4 text-cyan-400" />
              <span>Character Bible Specifications</span>
            </h4>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
              <div className="space-y-1 bg-slate-950/50 p-3 rounded-lg border border-slate-800/80">
                <div className="text-slate-500 text-[10px]">NAME & ARCHETYPE</div>
                <div className="text-slate-200 font-bold">ജോബ്‌ലെസ് ബോയ് (jobelessboy)</div>
                <div className="text-slate-400 text-[11px]">Cute 3D Pixar Kid Explorer & Science Sleuth</div>
              </div>

              <div className="space-y-1 bg-slate-950/50 p-3 rounded-lg border border-slate-800/80">
                <div className="text-slate-500 text-[10px]">ATTIRE & LOOK</div>
                <div className="text-cyan-400 font-semibold">Electric Blue Racing T-shirt & Magnifying Glass</div>
                <div className="text-slate-400 text-[11px]">Modeled after authentic reference photo with expressive brown eyes</div>
              </div>

              <div className="space-y-1 bg-slate-950/50 p-3 rounded-lg border border-slate-800/80">
                <div className="text-slate-500 text-[10px]">BACKGROUND PRESENTATION</div>
                <div className="text-amber-400 font-semibold">Dynamic Topic-Specific Visual Motion</div>
                <div className="text-slate-400 text-[11px]">Solar System, Mariana Trench, Pyramids & Brain Synapses</div>
              </div>

              <div className="space-y-1 bg-slate-950/50 p-3 rounded-lg border border-slate-800/80">
                <div className="text-slate-500 text-[10px]">NEURAL KID VOICE PROFILE</div>
                <div className="text-emerald-400 font-bold">ml-IN-MidhunNeural (+24Hz Pitch, +10% Rate)</div>
                <div className="text-slate-400 text-[11px]">High-reach energetic kid voice for maximum retention</div>
              </div>
            </div>
          </div>

          {/* Personality & Speech Ethics */}
          <div className="glass-panel p-5 rounded-xl space-y-3">
            <h4 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span>Narration & Ethical Guidelines</span>
            </h4>

            <ul className="space-y-2 text-xs text-slate-300">
              <li className="flex items-start gap-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 mt-0.5 flex-shrink-0" />
                <span><strong>Never Present Speculation as Fact:</strong> Distinguish scientific consensus from ongoing hypotheses and ancient mythological lore.</span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 mt-0.5 flex-shrink-0" />
                <span><strong>Authentic Malayalam Narration:</strong> Conversational tone avoiding stilted formal jargon while preserving rich vocabulary.</span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 mt-0.5 flex-shrink-0" />
                <span><strong>Zero-Cost Blender Integration:</strong> Ready for headless Blender Python execution (<code>scripts/blender_render.py</code>) with fallback to procedural motion graphics.</span>
              </li>
            </ul>
          </div>

        </div>

      </div>
    </div>
  );
};
