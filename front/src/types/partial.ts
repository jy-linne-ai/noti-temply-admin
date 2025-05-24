export interface PartialTemplate {
  id: string;
  name: string;
  description: string;
  content: string;
  dependencies: string[];
  version: string;
  layout: string;
  created_at: string;
  updated_at: string;
}

export interface ApiResponse<T> {
  data: T;
  message?: string;
} 