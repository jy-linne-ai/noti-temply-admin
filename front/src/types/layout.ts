import { Template } from './template';

export interface Layout {
  name: string;
  description: string;
  content: string;
  created_at: string;
  updated_at: string;
  version: string;
  templates?: Template[];
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