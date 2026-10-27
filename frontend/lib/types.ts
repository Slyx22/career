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
}

export interface ApiError {
  error: string;
}
