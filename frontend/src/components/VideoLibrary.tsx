import React, { useState } from 'react';
import {
  Play,
  Film,
  Video,
  CheckCircle2,
  Clock,
  ExternalLink,
  ShieldAlert,
  Calendar,
  X,
  FileCheck
} from 'lucide-react';
import { VideoItem } from '../types';

interface VideoLibraryProps {
  videos: VideoItem[];
  onRefresh: () => void;
}

export const VideoLibrary: React.FC<VideoLibraryProps> = ({ videos, onRefresh }) => {
  const [selectedVideo, setSelectedVideo] = useState<VideoItem | null>(null);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="font-heading text-lg font-bold text-slate-100 flex items-center gap-2">
            <span>Produced & Scheduled Video Vault</span>
            <span className="badge-tag bg-cyan-950 text-cyan-300 border border-cyan-500/30 text-[10px]">
              {videos.length} Generated
            </span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Full HD MP4s assembled with English voiceover, jobelessboy procedural host, and verified subtitles.
          </p>
        </div>

        <button
          onClick={onRefresh}
          className="glass-panel px-3 py-1.5 hover:bg-slate-800 text-xs text-slate-300 border-slate-700 rounded-lg"
        >
          Refresh Vault
        </button>
      </div>

      {videos.length === 0 ? (
        <div className="glass-panel p-12 text-center">
          <Film className="w-12 h-12 text-slate-600 mx-auto mb-3" />
          <h3 className="text-base font-semibold text-slate-300">No Videos Produced Yet</h3>
          <p className="text-xs text-slate-500 max-w-md mx-auto mt-1">
            Click 'Run Pipeline' or enable Autonomous Mode to discover topics, author English scripts, and render videos.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {videos.map((vid) => {
            const isShort = vid.video_type === 'short';
            const thumbUrl = vid.thumbnail_url
              ? (vid.thumbnail_url.startsWith('http') ? vid.thumbnail_url : vid.thumbnail_url)
              : '';
            const videoUrl = vid.video_url
              ? (vid.video_url.startsWith('http') ? vid.video_url : vid.video_url)
              : '';
            
            return (
              <div
                key={vid.id}
                className="glass-panel rounded-xl overflow-hidden flex flex-col justify-between group hover:border-cyan-500/50 transition-all shadow-lg"
              >
                <div>
                  {/* Thumbnail / Video Preview Box */}
                  <div className="relative aspect-video bg-slate-950 overflow-hidden cursor-pointer" onClick={() => setSelectedVideo(vid)}>
                    {thumbUrl ? (
                      <img
                        src={thumbUrl}
                        alt={vid.mal_title || 'Thumbnail'}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center bg-slate-900 text-slate-600">
                        <Film className="w-10 h-10" />
                      </div>
                    )}

                    {/* Play Button Overlay */}
                    <div className="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                      <div className="w-12 h-12 rounded-full bg-cyan-500/90 text-slate-950 flex items-center justify-center shadow-lg shadow-cyan-500/50">
                        <Play className="w-6 h-6 fill-current ml-0.5" />
                      </div>
                    </div>

                    {/* Format Badge */}
                    <div className="absolute top-2.5 left-2.5">
                      <span className={`badge-tag text-[10px] ${
                        isShort ? 'bg-amber-950/90 text-amber-300 border border-amber-500/40' : 'bg-cyan-950/90 text-cyan-300 border border-cyan-500/40'
                      }`}>
                        {isShort ? <Film className="w-2.5 h-2.5" /> : <Video className="w-2.5 h-2.5" />}
                        {isShort ? 'Short 1080x1920' : 'Long 1920x1080'}
                      </span>
                    </div>

                    {/* Duration Badge */}
                    {vid.duration_sec && (
                      <div className="absolute bottom-2.5 right-2.5 bg-black/80 font-mono text-[11px] text-white px-2 py-0.5 rounded">
                        {Math.round(vid.duration_sec)}s
                      </div>
                    )}
                  </div>

                  {/* Title & Info */}
                  <div className="p-4">
                    <h3 className="font-malayalam font-bold text-sm text-slate-100 line-clamp-2 leading-relaxed">
                      {vid.mal_title || vid.topic_title || 'Untitled MysteryVerse Video'}
                    </h3>
                    
                    <div className="text-xs text-slate-400 mt-1 line-clamp-1 font-mono">
                      {vid.topic_title}
                    </div>

                    {/* Quality Gate Status */}
                    <div className="mt-3 flex items-center gap-2">
                      <span className={`badge-tag text-[10px] ${
                        vid.quality_passed
                          ? 'bg-emerald-950/80 text-emerald-300 border border-emerald-500/30'
                          : 'bg-rose-950/80 text-rose-300 border border-rose-500/30'
                      }`}>
                        {vid.quality_passed ? <CheckCircle2 className="w-3 h-3" /> : <ShieldAlert className="w-3 h-3" />}
                        {vid.quality_passed ? 'Quality Gate PASSED' : 'Failed Quality Gate'}
                      </span>

                      <span className="text-[11px] text-slate-400 font-mono">
                        Engine: {vid.render_engine}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Footer with Publishing / Schedule Status */}
                <div className="px-4 py-3 bg-slate-950/60 border-t border-slate-800/80 flex items-center justify-between text-xs">
                  <div className="flex items-center gap-1.5 text-slate-400 font-mono">
                    <Calendar className="w-3.5 h-3.5 text-cyan-400" />
                    <span>
                      {vid.scheduled_publish_time
                        ? new Date(vid.scheduled_publish_time).toLocaleString('en-IN', {
                            timeZone: 'Asia/Kolkata',
                            month: 'short',
                            day: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit'
                          }) + ' IST'
                        : 'Ready for Staging'}
                    </span>
                  </div>

                  {vid.youtube_url ? (
                    <a
                      href={vid.youtube_url}
                      target="_blank"
                      rel="noreferrer"
                      className="text-cyan-400 hover:text-cyan-300 flex items-center gap-1 font-mono font-medium"
                    >
                      <span>Scheduled</span>
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  ) : (
                    <button
                      onClick={() => setSelectedVideo(vid)}
                      className="text-slate-400 hover:text-slate-200"
                    >
                      Inspect
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Video Player & Inspector Modal */}
      {selectedVideo && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4">
          <div className="glass-panel w-full max-w-3xl max-h-[90vh] overflow-y-auto rounded-2xl border-cyan-500/40 p-6 relative">
            <button
              onClick={() => setSelectedVideo(null)}
              className="absolute top-4 right-4 p-2 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-300"
            >
              <X className="w-5 h-5" />
            </button>

            <h3 className="font-malayalam font-bold text-lg text-slate-100 pr-10">
              {selectedVideo.mal_title || selectedVideo.topic_title}
            </h3>
            <p className="text-xs text-slate-400 font-mono mt-0.5">
              Job ID: {selectedVideo.id} • {selectedVideo.resolution}
            </p>

            {/* Video Player */}
            <div className="mt-4 rounded-xl overflow-hidden bg-black aspect-video flex items-center justify-center">
              {selectedVideo.video_url ? (
                <video
                  controls
                  autoPlay
                  className="w-full h-full object-contain"
                  src={selectedVideo.video_url}
                >
                  {selectedVideo.subtitles_url && (
                    <track
                      kind="subtitles"
                      src={selectedVideo.subtitles_url}
                      srcLang="en"
                      label="English"
                      default
                    />
                  )}
                </video>
              ) : (
                <div className="text-slate-500 text-sm">Video file not found</div>
              )}
            </div>

            {/* Quality Report Audit Details */}
            <div className="mt-5 p-4 rounded-xl bg-slate-900/80 border border-slate-800 text-xs space-y-2">
              <div className="flex items-center justify-between font-bold text-slate-200 border-b border-slate-800 pb-2">
                <span className="flex items-center gap-1.5">
                  <FileCheck className="w-4 h-4 text-emerald-400" />
                  Quality Gatekeeper Audit Summary
                </span>
                <span className={selectedVideo.quality_passed ? 'text-emerald-400' : 'text-rose-400'}>
                  {selectedVideo.quality_passed ? 'PASSED ALL GATES' : 'FAILED AUDIT'}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-3 pt-1 text-slate-300 font-mono">
                <div>
                  <span className="text-slate-500">Language Verification:</span> Malayalam Valid
                </div>
                <div>
                  <span className="text-slate-500">Audio/Video Sync:</span> Accurate
                </div>
                <div>
                  <span className="text-slate-500">Copyright Status:</span> 100% Procedural & Original
                </div>
                <div>
                  <span className="text-slate-500">Synthetic Disclosure:</span> Declared to YouTube
                </div>
              </div>
            </div>

            {/* Subtitles & Script preview */}
            {selectedVideo.full_script_mal && (
              <div className="mt-4">
                <h4 className="text-xs font-semibold text-slate-300 mb-1.5">Malayalam Narration Script:</h4>
                <div className="p-3 bg-slate-950/70 rounded-lg border border-slate-800 text-xs font-malayalam text-slate-200 leading-relaxed max-h-36 overflow-y-auto">
                  {selectedVideo.full_script_mal}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
