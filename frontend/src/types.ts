export interface ChannelInfo {
  channel_id?: string;
  title?: string;
  handle?: string;
  custom_url?: string;
  subscriber_count?: number;
  video_count?: number;
  view_count?: number;
  is_target_match?: boolean;
  authenticated?: boolean;
  mode?: string;
}

export interface MonthlyProgress {
  shorts_produced: number;
  shorts_target: number;
  shorts_pct: number;
  longs_produced: number;
  longs_target: number;
  longs_pct: number;
  total_produced: number;
  total_target: number;
}

export interface PipelineCounts {
  total_topics: number;
  discovered_topics: number;
  total_scripts: number;
  rendering_jobs: number;
  ready_for_upload: number;
  scheduled_videos: number;
  failed_jobs: number;
}

export interface SystemStatus {
  killswitch_active: boolean;
  autonomous_scheduler_active: boolean;
  auto_publish_enabled: boolean;
  ffmpeg_detected: boolean;
  ffmpeg_path?: string;
  blender_detected: boolean;
  blender_path?: string;
  disk_free_gb: number;
  daily_quota_used: number;
  daily_quota_limit: number;
}

export interface SystemLog {
  id: number;
  level: string;
  source: string;
  message: string;
  details_json?: string;
  created_at: string;
}

export interface DashboardStats {
  channel: {
    name: string;
    handle: string;
    is_connected: boolean;
    connected_info: ChannelInfo;
  };
  monthly_progress: MonthlyProgress;
  pipeline_counts: PipelineCounts;
  system_status: SystemStatus;
  character: {
    name_malayalam: string;
    name_english: string;
    title: string;
    archetype: string;
    channel: string;
    tagline: string;
  };
  recent_logs: SystemLog[];
}

export interface TopicItem {
  id: string;
  title: string;
  mal_title: string;
  core_question?: string;
  category: string;
  format: 'short' | 'long';
  potential_interest_score: number;
  source_references: string[];
  retrieved_at: string;
  fact_status: string;
  fact_confidence: number;
  originality_score: number;
  originality_explanation?: string;
  status: string;
  created_at: string;
}

export interface SceneCue {
  scene_number: number;
  duration_sec: number;
  visual_description: string;
  camera_movement: string;
  character_expression: string;
  character_pose: string;
  background_theme: string;
  speech_segment_mal: string;
}

export interface ScriptItem {
  id: string;
  topic_id: string;
  topic_title?: string;
  mal_title?: string;
  category?: string;
  format: 'short' | 'long';
  mal_hook: string;
  mal_content: string;
  mal_conclusion: string;
  full_script_mal: string;
  scenes: SceneCue[];
  estimated_duration_sec: number;
  word_count: number;
  model_used: string;
  status: string;
  created_at: string;
}

export interface VideoItem {
  id: string;
  title?: string;
  script_id: string;
  topic_id: string;
  topic_title?: string;
  mal_title?: string;
  full_script_mal?: string;
  video_type: 'short' | 'long';
  resolution: string;
  video_path?: string;
  video_url?: string;
  thumbnail_path?: string;
  thumbnail_url?: string;
  subtitles_path?: string;
  subtitles_url?: string;
  duration_sec?: number;
  render_engine: string;
  status: string;
  quality_passed: boolean;
  quality_report?: Record<string, any>;
  youtube_video_id?: string;
  youtube_url?: string;
  scheduled_publish_time?: string;
  upload_status?: string;
  error_message?: string;
  created_at: string;
  completed_at?: string;
}

export interface ChannelAuditData {
  is_authorized: boolean;
  target_channel_name: string;
  target_channel_handle: string;
  target_channel_url: string;
  connected_channel: ChannelInfo;
  target_matched: boolean;
  api_accessible_settings: Record<string, string>;
  manual_action_items: Array<{
    setting: string;
    status: string;
    reason: string;
    instruction: string;
  }>;
}

export interface MonetisationData {
  subscriber_count: number;
  subscribers_required: number;
  subscribers_progress_pct: number;
  watch_hours: number;
  watch_hours_required: number;
  watch_hours_progress_pct: number;
  shorts_views_90d: number;
  shorts_views_required: number;
  shorts_views_progress_pct: number;
  is_eligible_standard: boolean;
  is_eligible_shorts: boolean;
  monetisation_status: string;
  published_videos_count: number;
  educational_notes: string[];
}
