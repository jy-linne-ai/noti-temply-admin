import { TemplateComponent } from './template';

export interface Layout {
  name: string;
  description: string;
  content: string;
  created_at: string;
  created_by: string | null;
  updated_at: string;
  updated_by: string | null;
  version: string;
  templates?: TemplateComponent[];
}

export interface CreateLayoutRequest {
  name: string;
  description: string;
  content: string;
}

export interface UpdateLayoutRequest {
  description?: string;
  content?: string;
}

export interface ApiResponse<T> {
  data: T;
  message?: string;
} 