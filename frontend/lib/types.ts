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
  /** "required" by law or registration; "usual" = employers usually ask. Older results have none (required). */
  kind?: "required" | "usual";
}

export interface PrivacyWarning {
  key: string;
  label: string;
}

export interface CvBasic {
  key: string;
  label: string;
  ok: boolean;
  fix: string;
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
  privacy_warnings?: PrivacyWarning[];
  privacy_advice?: string | null;
  cv_basics?: CvBasic[];
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
}

export interface ApiError {
  error: string;
}
