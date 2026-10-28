export interface Career {
  slug: string;
  name: string;
  description: string;
}

/** South African (OFO 2021) job title linked to a career: t=title, a=other names, s=career slug. */
export interface SaTitle {
  t: string;
  a: string[];
  s: string;
}

export interface SaRequirement {
  key: string;
  label: string;
  detail: string;
  found_in_cv: boolean;
}

export interface SkillBreakdownItem {
  slug: string;
  name: string;
  category: string;
  present: boolean;
  score_percent: number;
  importance_level?: "essential" | "important" | "useful" | "";
  is_tool?: boolean;
  tip?: string | null;
}

export interface AnalysisResult {
  analysis_id: string;
  score: number;
  career: string;
  career_slug: string;
  onet_career?: string | null;
  first_name: string;
  surname: string;
  strengths: string[];
  gaps: string[];
  skill_breakdown: SkillBreakdownItem[];
  recommendations: string[];
  benchmark_disclaimer: string;
  sa_requirements?: SaRequirement[];
  band?: string;
  band_label?: string;
  points_to_seal?: number;
  created_at: string;
}

export interface CertificateResult {
  certificate_id: string;
  first_name: string;
  surname: string;
  career: string;
  score: number;
  issued_at: string;
  verify_path: string;
}

export interface CertificateVerification {
  verified: boolean;
  certificate_id?: string;
  first_name?: string;
  surname?: string;
  career?: string;
  score?: number;
  issued_at?: string;
  valid_until?: string;
  expired?: boolean;
  issuer?: string;
  method_version?: string;
  band?: string;
  band_label?: string;
  seal?: boolean;
}

export interface ApiError {
  error: string;
}
