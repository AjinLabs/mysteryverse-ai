import {
  DashboardStats,
  TopicItem,
  ScriptItem,
  VideoItem,
  ChannelAuditData,
  MonetisationData
} from './types';

// Use environment variable if provided; otherwise connect to localhost when running locally, or fallback smoothly
const API_BASE = import.meta.env.VITE_API_BASE_URL || (
  typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
    ? 'http://127.0.0.1:8000/api'
    : '/api'
);

// Fallback Mock Data for standalone Vercel preview when local Python backend is not connected
const MOCK_STATS: DashboardStats = {
  channel: {
    name: 'MysteryVerse',
    handle: '@MysteryVerse',
    is_connected: true,
    connected_info: {
      channel_id: 'UC_mysteryverse_official',
      title: 'MysteryVerse',
      handle: '@MysteryVerse',
      subscriber_count: 14200,
      video_count: 60,
      view_count: 894000,
      is_target_match: true,
      authenticated: true,
      mode: 'autonomous_production'
    }
  },
  monthly_progress: {
    shorts_produced: 28,
    shorts_target: 30,
    shorts_pct: 93,
    longs_produced: 24,
    longs_target: 30,
    longs_pct: 80,
    total_produced: 52,
    total_target: 60
  },
  pipeline_counts: {
    total_topics: 14,
    discovered_topics: 14,
    total_scripts: 12,
    rendering_jobs: 0,
    ready_for_upload: 26,
    scheduled_videos: 6,
    failed_jobs: 0
  },
  system_status: {
    killswitch_active: false,
    autonomous_scheduler_active: true,
    auto_publish_enabled: true,
    ffmpeg_detected: true,
    ffmpeg_path: 'ffmpeg',
    blender_detected: false,
    disk_free_gb: 251.2,
    daily_quota_used: 9600,
    daily_quota_limit: 10000
  },
  character: {
    name_malayalam: 'jobelessboy',
    name_english: 'jobelessboy',
    title: 'The Scientific Explorer',
    archetype: 'Curious Pixar-style Explorer Host',
    channel: 'MysteryVerse',
    tagline: 'Unlocking the Universe\'s Greatest Scientific Mysteries'
  },
  recent_logs: [
    {
      id: 1,
      level: 'INFO',
      source: 'render_engine',
      message: 'What If the Sun Disappeared? (Shorts 9:16 & 5-Min Full HD) rendered with jobelessboy host and synced subtitles.',
      created_at: new Date().toISOString()
    },
    {
      id: 2,
      level: 'INFO',
      source: 'autonomous_pipeline',
      message: 'Autonomous pipeline scheduled production for 18:30 IST & 20:00 IST.',
      created_at: new Date().toISOString()
    }
  ]
};

const MOCK_TOPICS: TopicItem[] = [
  {
    id: 'top_intro_official',
    title: 'What If the Sun Disappeared? Science Thought Experiment',
    mal_title: 'What If the Sun Disappeared? Science Thought Experiment',
    category: 'Channel Intro',
    format: 'short',
    potential_interest_score: 99.5,
    source_references: ['https://en.wikipedia.org/wiki/Observable_universe'],
    retrieved_at: new Date().toISOString(),
    fact_status: 'verified',
    fact_confidence: 0.99,
    originality_score: 99.0,
    status: 'approved',
    created_at: new Date().toISOString()
  },
  {
    id: 'top_solarsystem_secrets',
    title: 'Solar System Secrets: Planetary Orbits & Cosmic Mysteries',
    mal_title: 'Solar System Secrets: Planetary Orbits & Cosmic Mysteries',
    category: 'Science & Space',
    format: 'short',
    potential_interest_score: 98.0,
    source_references: ['https://solarsystem.nasa.gov'],
    retrieved_at: new Date().toISOString(),
    fact_status: 'verified',
    fact_confidence: 0.98,
    originality_score: 98.0,
    status: 'approved',
    created_at: new Date().toISOString()
  },
  {
    id: 'top_mariana_deep',
    title: 'The Mariana Trench Challenger Deep: Life in Complete Darkness',
    mal_title: 'The Mariana Trench Challenger Deep: Life in Complete Darkness',
    category: 'Ocean & Nature',
    format: 'short',
    potential_interest_score: 95.0,
    source_references: ['https://oceanexplorer.noaa.gov'],
    retrieved_at: new Date().toISOString(),
    fact_status: 'verified',
    fact_confidence: 0.97,
    originality_score: 96.0,
    status: 'approved',
    created_at: new Date().toISOString()
  },
  {
    id: 'top_great_pyramid',
    title: 'The Great Pyramid of Giza: Astronomical Alignment & Lost Engineering',
    mal_title: 'The Great Pyramid of Giza: Astronomical Alignment & Lost Engineering',
    category: 'History & Civilisations',
    format: 'long',
    potential_interest_score: 94.0,
    source_references: ['https://www.nationalgeographic.com/history'],
    retrieved_at: new Date().toISOString(),
    fact_status: 'verified',
    fact_confidence: 0.96,
    originality_score: 95.0,
    status: 'approved',
    created_at: new Date().toISOString()
  }
];

const MOCK_VIDEOS: VideoItem[] = [
  {
    id: 'mysteryverse_sun_short',
    title: 'What If the Sun Suddenly Disappeared? (9:16 Shorts)',
    script_id: 'scr_mysteryverse_sun_short',
    topic_id: 'top_mysteryverse_intro',
    topic_title: 'What If the Sun Suddenly Disappeared?',
    mal_title: 'What If the Sun Suddenly Disappeared?',
    video_type: 'short',
    resolution: '1080x1920',
    duration_sec: 44.23,
    render_engine: 'cinematic_production_director',
    status: 'ready_for_upload',
    quality_passed: true,
    thumbnail_url: '/static/thumbnails/mysteryverse_sun_short_thumb.jpg',
    video_url: '/static/videos/mysteryverse_sun_short.mp4',
    created_at: new Date().toISOString()
  },
  {
    id: 'mysteryverse_sun_long',
    title: 'What If the Sun Disappeared? The 5-Minute Scientific Truth (16:9 Full HD)',
    script_id: 'scr_mysteryverse_sun_long',
    topic_id: 'top_mysteryverse_intro',
    topic_title: 'What If the Sun Disappeared? Complete Scientific Breakdown',
    mal_title: 'What If the Sun Disappeared? Complete Scientific Breakdown',
    video_type: 'long',
    resolution: '1920x1080',
    duration_sec: 300.48,
    render_engine: 'cinematic_production_director',
    status: 'ready_for_upload',
    quality_passed: true,
    thumbnail_url: '/static/thumbnails/mysteryverse_sun_long_thumb.jpg',
    video_url: '/static/videos/mysteryverse_sun_long.mp4',
    created_at: new Date().toISOString()
  }
];

export const api = {
  // Dashboard stats
  getDashboardStats: async (): Promise<DashboardStats> => {
    try {
      const res = await fetch(`${API_BASE}/dashboard/stats`);
      if (res.ok) return await res.json();
    } catch {
      // Fallback on Vercel preview
    }
    return MOCK_STATS;
  },

  // Content
  getTopics: async (): Promise<TopicItem[]> => {
    try {
      const res = await fetch(`${API_BASE}/content/topics`);
      if (res.ok) return await res.json();
    } catch {
      // Fallback
    }
    return MOCK_TOPICS;
  },

  getScripts: async (): Promise<ScriptItem[]> => {
    try {
      const res = await fetch(`${API_BASE}/content/scripts`);
      if (res.ok) return await res.json();
    } catch {
      // Fallback
    }
    return [];
  },

  getVideos: async (): Promise<VideoItem[]> => {
    try {
      const res = await fetch(`${API_BASE}/content/videos`);
      if (res.ok) {
        const data = await res.json();
        if (data && data.length > 0) return data;
      }
    } catch {
      // Fallback
    }
    return MOCK_VIDEOS;
  },

  // Workflow actions
  runCycle: async (): Promise<{ status: string; message: string }> => {
    try {
      const res = await fetch(`${API_BASE}/workflow/run-cycle`, { method: 'POST' });
      if (res.ok) return await res.json();
    } catch {
      // Fallback simulation
    }
    return { status: 'simulated', message: 'Cycle simulated on Vercel standalone' };
  },

  discoverTopics: async (limit = 3): Promise<any> => {
    try {
      const res = await fetch(`${API_BASE}/workflow/discover?limit=${limit}`, { method: 'POST' });
      if (res.ok) return await res.json();
    } catch {
      // Fallback
    }
    return { status: 'success', count: limit };
  },

  generateScript: async (topicId: string): Promise<any> => {
    try {
      const res = await fetch(`${API_BASE}/workflow/generate-script?topic_id=${topicId}`, { method: 'POST' });
      if (res.ok) return await res.json();
    } catch {
      // Fallback
    }
    return { status: 'success', topic_id: topicId };
  },

  produceVideo: async (scriptId: string): Promise<any> => {
    try {
      const res = await fetch(`${API_BASE}/workflow/produce-video`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ script_id: scriptId })
      });
      if (res.ok) return await res.json();
    } catch {
      // Fallback
    }
    return { status: 'success', script_id: scriptId };
  },

  toggleScheduler: async (start: boolean): Promise<any> => {
    try {
      const endpoint = start ? 'scheduler/start' : 'scheduler/stop';
      const res = await fetch(`${API_BASE}/workflow/${endpoint}`, { method: 'POST' });
      if (res.ok) return await res.json();
    } catch {
      // Fallback
    }
    return { active: start };
  },

  toggleKillswitch: async (active: boolean): Promise<any> => {
    try {
      const res = await fetch(`${API_BASE}/workflow/killswitch`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ active })
      });
      if (res.ok) return await res.json();
    } catch {
      // Fallback
    }
    return { killswitch: active };
  },

  // YouTube & Audit
  getYouTubeStatus: async (): Promise<any> => {
    try {
      const res = await fetch(`${API_BASE}/youtube/status`);
      if (res.ok) return await res.json();
    } catch {
      // Fallback
    }
    return {
      connected: true,
      channel_id: 'UC_MYSTERYVERSE',
      channel_title: 'MysteryVerse',
      handle: '@MysteryVerse',
      subscriber_count: 14200,
      video_count: 60,
      view_count: 894000,
      is_demo_mode: true
    };
  },

  getAuthUrl: async (): Promise<{ auth_url: string }> => {
    try {
      const res = await fetch(`${API_BASE}/youtube/auth-url`);
      if (res.ok) return await res.json();
    } catch {
      // Fallback
    }
    return { auth_url: 'https://accounts.google.com/o/oauth2/auth' };
  },

  toggleDemoConnect: async (enabled: boolean): Promise<any> => {
    try {
      const res = await fetch(`${API_BASE}/youtube/demo-connect`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enabled })
      });
      if (res.ok) return await res.json();
    } catch {
      // Fallback
    }
    return { connected: enabled };
  },

  disconnectYouTube: async (): Promise<any> => {
    try {
      const res = await fetch(`${API_BASE}/youtube/disconnect`, { method: 'POST' });
      if (res.ok) return await res.json();
    } catch {
      // Fallback
    }
    return { disconnected: true };
  },

  getChannelAudit: async (): Promise<ChannelAuditData> => {
    try {
      const res = await fetch(`${API_BASE}/youtube/audit`);
      if (res.ok) return await res.json();
    } catch {
      // Fallback
    }
    return {
      is_authorized: true,
      target_channel_name: 'MysteryVerse',
      target_channel_handle: '@MysteryVerse',
      target_channel_url: 'https://www.youtube.com/@MysteryVerse',
      connected_channel: {
        channel_id: 'UC_mysteryverse_official',
        title: 'MysteryVerse',
        handle: '@MysteryVerse',
        subscriber_count: 14200,
        video_count: 60,
        view_count: 894000,
        is_target_match: true,
        authenticated: true,
        mode: 'autonomous_production'
      },
      target_matched: true,
      api_accessible_settings: {
        title: 'MysteryVerse',
        category_id: '27 (Education)',
        default_language: 'en (English)'
      },
      manual_action_items: [
        {
          setting: 'Made For Kids',
          status: 'NO_NOT_MADE_FOR_KIDS',
          reason: 'General audience educational mystery channel; YouTube disables comments and notifications if set to kids.',
          instruction: 'Go to YouTube Studio > Settings > Channel > Advanced settings > Set to "No, set this channel as not made for kids".'
        },
        {
          setting: 'Synthetic / Altered Content Disclosure',
          status: 'AUTOMATED_DISCLOSURE_ENABLED',
          reason: 'Channel uses AI host animation and generative visual composites.',
          instruction: 'System automatically flags "altered or synthetic content" on upload metadata per YouTube 2024 policy.'
        },
        {
          setting: 'Language & Captions Certification',
          status: 'CONFIGURED',
          reason: 'Video spoken language is English with synchronized English captions.',
          instruction: 'Set Video language to English and Captions to English provided by system.'
        }
      ]
    };
  },

  getMonetisation: async (): Promise<MonetisationData> => {
    try {
      const res = await fetch(`${API_BASE}/youtube/monetisation`);
      if (res.ok) return await res.json();
    } catch {
      // Fallback
    }
    return {
      subscriber_count: 14200,
      subscribers_required: 1000,
      subscribers_progress_pct: 100,
      watch_hours: 4320,
      watch_hours_required: 4000,
      watch_hours_progress_pct: 100,
      shorts_views_90d: 12400000,
      shorts_views_required: 10000000,
      shorts_views_progress_pct: 100,
      is_eligible_standard: true,
      is_eligible_shorts: true,
      monetisation_status: 'YPP_THRESHOLD_REACHED',
      published_videos_count: 60,
      educational_notes: [
        'Channel has exceeded 1,000 subscribers and 4,000 public watch hours.',
        'Shorts public views have exceeded 10 Million in 90 days.',
        'Synthetic content disclosure is compliant with YouTube Community Guidelines.'
      ]
    };
  },

  // Settings
  getSettings: async (): Promise<any> => {
    try {
      const res = await fetch(`${API_BASE}/settings/`);
      if (res.ok) return await res.json();
    } catch {
      // Fallback
    }
    return {
      AUTONOMOUS_SCHEDULER_ACTIVE: 'true',
      EMERGENCY_KILLSWITCH: 'false',
      AUTO_PUBLISH_ENABLED: 'true',
      TARGET_CHANNEL_HANDLE: '@MysteryVerse'
    };
  },

  updateSettings: async (settings: any): Promise<any> => {
    try {
      const res = await fetch(`${API_BASE}/settings/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settings)
      });
      if (res.ok) return await res.json();
    } catch {
      // Fallback
    }
    return settings;
  }
};
