export interface User {
  id: string;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  full_name: string;
  short_name: string;
  avatar_url: string;
  company_name: string;
  subscription_tier: 'free' | 'pro' | 'enterprise';
  monthly_proposal_quota: number;
  proposals_generated_this_month: number;
  remaining_quota: number;
  has_reached_quota: boolean;
  is_pro: boolean;
  is_onboarded: boolean;
  created_at: string;
}

export interface Proposal {
  id: string;
  title: string;
  client_name: string;
  client_company: string;
  client_email: string;
  job_description: string;
  job_platform: string;
  status: 'draft' | 'generated' | 'edited' | 'sent' | 'accepted' | 'rejected' | 'archived';
  status_color: string;
  tone_used: string;
  word_count: number;
  generated_content: { sections: { name: string; content: string }[] };
  final_content: string;
  is_favorite: boolean;
  folder: string;
  tags: string[];
  template_name: string | null;
  ai_cost_usd: string;
  rating: number | null;
  sent_at: string | null;
  accepted_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface Lead {
  id: string;
  full_name: string;
  initials: string;
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  company: string;
  job_title: string;
  source: string;
  status: string;
  status_color: string;
  priority: string;
  priority_color: string;
  estimated_value: string | null;
  currency: string;
  is_hot: boolean;
  tags: string[];
  score_summary: { total: number; tier: string; change: number } | null;
  days_since_contact: number | null;
  next_follow_up_at: string | null;
  last_contact_at: string | null;
  industry: string;
  company_size: string;
  notes: string;
  created_at: string;
}

export interface LeadScore {
  total_score: number;
  score_tier: 'cold' | 'warm' | 'hot' | 'qualified';
  score_change: number;
  engagement_score: number;
  recency_score: number;
  frequency_score: number;
  depth_score: number;
  demographic_score: number;
  intent_score: number;
  breakdown: Record<string, { score: number; weight: number; weighted: number }>;
  trend: { direction: string; change: number; history: { date: string; score: number }[] };
  recommendations: { type: string; priority: string; message: string }[];
}

export interface LeadActivity {
  id: string;
  activity_type: string;
  description: string;
  activity_icon: string;
  activity_color: string;
  is_system_generated: boolean;
  metadata: Record<string, unknown>;
  created_at: string;
}

export interface Template {
  id: string;
  name: string;
  description: string;
  category: string;
  tone: string;
  usage_count: number;
  average_rating: string;
  is_favorite: boolean;
  is_system_template: boolean;
  section_count: number;
  tags: string[];
  created_at: string;
}

export interface Notification {
  id: string;
  notification_type: string;
  title: string;
  message: string;
  is_read: boolean;
  action_url: string;
  created_at: string;
}

export interface PaginatedResponse<T> {
  count: number;
  total_pages: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface DashboardStats {
  leads: { total: number; active: number; this_month: number; last_month: number; mom_change: number };
  conversion: { rate: number; closed_won: number; closed_total: number };
  pipeline: { value: number; currency: string };
  proposals: { generated: number; quota: number; remaining: number; this_month: number; accepted_this_month: number };
  follow_ups: { overdue: number };
  score_distribution: Record<string, number>;
}