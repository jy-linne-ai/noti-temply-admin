export interface PartialTemplate {
  name: string;
  description?: string;
  content?: string;
  dependencies?: string[];
  version: string;
  layout: string;
  created_at?: string;
  created_by?: string;
  updated_at?: string;
  updated_by?: string;
  depth?: number;
  isAdded?: boolean;
}

export interface ApiResponse<T> {
  data: T;
  message?: string;
} 