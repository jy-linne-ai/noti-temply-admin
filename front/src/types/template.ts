export interface BaseEntity {
  id: string;
  name: string;
  description: string;
  version: string;
  createdAt: string;
  updatedAt: string;
}

export interface Layout extends BaseEntity {
  slots: {
    [key: string]: boolean;
  };
  template: string;  // 레이아웃 HTML 템플릿
}

export interface Part extends BaseEntity {
  parent: string | null;
  children: string[];
  variables: Variable[];
  template: string;  // 파츠 HTML 템플릿
}

export interface Variable {
  name: string;
  type: 'string' | 'number' | 'date' | 'boolean';
  required: boolean;
  defaultValue?: any;
  description?: string;
}

export interface Template {
  description: string | null;
  created_at: string | null;
  created_by: string | null;
  updated_at: string | null;
  updated_by: string | null;
  template: string;
  component: string;
  layout: string | null;
  partials: string[];
  content: string;
  dependencies?: string[];  // 의존성 목록
  isMapped?: boolean;
}

export interface CreateTemplateRequest {
  name: string;
  description: string;
}

export interface UpdateTemplateRequest {
  description?: string;
  content?: string;
  partials?: string[];
}

export interface TemplateItem {
  id: string;
  name: string;
  description: string;
  content: string;
  created_at: string;
  updated_at: string;
}

export interface CreateTemplateItemRequest {
  name: string;
  description: string;
  content: string;
}

export interface UpdateTemplateItemRequest {
  description?: string;
  content?: string;
}

// API 응답 타입
export interface ApiResponse<T> {
  data: T;
  message?: string;
  error?: string;
}

// 페이지네이션 응답 타입
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
} 