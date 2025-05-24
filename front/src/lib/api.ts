import axios from 'axios';
import { Version } from '@/types/version';
import { Layout, ApiResponse as LayoutApiResponse } from '@/types/layout';
import { Template } from '@/types/template';
import { PartialTemplate, ApiResponse as PartialApiResponse } from '@/types/partial';

interface ApiResponse<T> {
  data: T;
  message?: string;
  status: number;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 버전 체크 함수
export const checkVersion = async (version: string) => {
  try {
    const response = await api.get(`/api/v1/versions/${version}`);
    return response.data;
  } catch (error) {
    throw error;
  }
};

// 요청 인터셉터
api.interceptors.request.use(
  (config) => {
    console.log('API Request:', {
      method: config.method,
      url: config.url,
      params: config.params,
      data: config.data,
    });
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// 응답 인터셉터
api.interceptors.response.use(
  (response) => {
    console.log('API Response:', {
      status: response.status,
      data: response.data,
      dataType: typeof response.data,
      hasData: response.data ? 'data' in response.data : false,
      dataKeys: response.data ? Object.keys(response.data) : [],
    });
    return response;
  },
  (error) => {
    console.error('API Response Error:', {
      status: error.response?.status,
      data: error.response?.data,
      message: error.message,
    });
    return Promise.reject(error);
  }
);

export interface ApiClient {
  // 버전 관련 API
  getVersions: () => Promise<Version[]>;
  getVersion: (version: string) => Promise<Version>;
  createVersion: (version: string) => Promise<Version>;
  updateVersion: (oldVersion: string, newVersion: string) => Promise<Version>;
  deleteVersion: (version: string) => Promise<void>;
  
  // 레이아웃 관련 API
  getLayouts: (version: string) => Promise<Layout[]>;
  getLayout: (version: string, layout: string) => Promise<Layout>;
  createLayout: (version: string, data: Partial<Layout>) => Promise<Layout>;
  updateLayout: (version: string, layout: string, data: Partial<Layout>) => Promise<Layout>;
  deleteLayout: (version: string, layout: string) => Promise<void>;
  
  // 템플릿 관련 API
  getTemplates: (version: string) => Promise<Template[]>;
  getTemplate: (version: string, template: string) => Promise<Template>;
  createTemplate: (version: string, data: Partial<Template>) => Promise<Template>;
  updateTemplate: (version: string, template: string, data: Partial<Template>) => Promise<Template>;
  deleteTemplate: (version: string, template: string) => Promise<void>;

  getLayoutSchema: (version: string, layoutName: string) => Promise<any>;
  renderLayout: (version: string, layoutName: string, data: Record<string, any>) => Promise<string>;

  // 파셜 관련 API
  getPartials: (version: string, isRoot: boolean) => Promise<PartialTemplate[]>;
  getAllPartials: (version: string) => Promise<PartialTemplate[]>;
  getPartial: (version: string, partial: string) => Promise<PartialTemplate>;
  createPartial: (version: string, data: Partial<PartialTemplate>) => Promise<PartialTemplate>;
  updatePartial: (version: string, partial: string, data: Partial<PartialTemplate>) => Promise<PartialTemplate>;
  deletePartial: (version: string, partial: string) => Promise<void>;
  getPartialChildren: (version: string, partial: string) => Promise<PartialTemplate[]>;
}

export function useApi(): ApiClient {
  return {
    // 버전 관련 API
    getVersions: () => api.get<Version[]>('/api/v1/versions').then(res => res.data),
    getVersion: (version: string) => api.get<Version>(`/api/v1/versions/${version}`).then(res => res.data),
    createVersion: (version: string) => api.post<Version>('/api/v1/versions', { version }).then(res => res.data),
    updateVersion: (oldVersion: string, newVersion: string) => 
      api.put<Version>(`/api/v1/versions/${oldVersion}`, { version: newVersion }).then(res => res.data),
    deleteVersion: (version: string) => api.delete(`/api/v1/versions/${version}`),
    
    // 레이아웃 관련 API
    getLayouts: (version: string) => api.get<Layout[]>(`/api/v1/versions/${version}/layouts`).then(res => res.data),
    getLayout: (version: string, layout: string) => api.get<Layout>(`/api/v1/versions/${version}/layouts/${layout}`).then(res => res.data),
    createLayout: (version: string, data: Partial<Layout>) => api.post<Layout>(`/api/v1/versions/${version}/layouts`, data).then(res => res.data),
    updateLayout: (version: string, layout: string, data: Partial<Layout>) => 
      api.put<Layout>(`/api/v1/versions/${version}/layouts/${layout}`, data).then(res => res.data),
    deleteLayout: (version: string, layout: string) => 
      api.delete(`/api/v1/versions/${version}/layouts/${layout}`).then(() => {}),
    
    // 템플릿 관련 API
    getTemplates: (version: string) => api.get<Template[]>(`/api/v1/versions/${version}/templates`).then(res => res.data),
    getTemplate: (version: string, template: string) => 
      api.get<Template>(`/api/v1/versions/${version}/templates/${template}`).then(res => res.data),
    createTemplate: (version: string, data: Partial<Template>) => 
      api.post<Template>(`/api/v1/versions/${version}/templates`, data).then(res => res.data),
    updateTemplate: (version: string, template: string, data: Partial<Template>) => 
      api.put<Template>(`/api/v1/versions/${version}/templates/${template}`, data).then(res => res.data),
    deleteTemplate: (version: string, template: string) => 
      api.delete(`/api/v1/versions/${version}/templates/${template}`),

    getLayoutSchema: async (version: string, layoutName: string) => {
      const response = await api.get<ApiResponse<any>>(`/api/v1/versions/${version}/layouts/${layoutName}/schema`);
      return response.data.data;
    },

    renderLayout: async (version: string, layoutName: string, data: Record<string, any>) => {
      const response = await api.post<ApiResponse<string>>(`/api/v1/versions/${version}/layouts/${layoutName}/render`, data);
      return response.data.data;
    },

    // 파셜 관련 API
    getPartials: async (version: string, isRoot: boolean) => {
      const response = await api.get<PartialTemplate[]>(`/api/v1/versions/${version}/partials?is_root=${isRoot}`);
      return response.data;
    },
    getAllPartials: async (version: string) => {
      const response = await api.get<PartialTemplate[]>(`/api/v1/versions/${version}/partials`);
      return response.data;
    },
    getPartial: (version: string, partial: string) => 
      api.get<PartialTemplate>(`/api/v1/versions/${version}/partials/${partial}`).then(res => res.data),
    createPartial: (version: string, data: Partial<PartialTemplate>) => 
      api.post<PartialTemplate>(`/api/v1/versions/${version}/partials`, data).then(res => res.data),
    updatePartial: (version: string, partial: string, data: Partial<PartialTemplate>) => 
      api.put<PartialTemplate>(`/api/v1/versions/${version}/partials/${partial}`, data).then(res => res.data),
    deletePartial: (version: string, partial: string) => 
      api.delete(`/api/v1/versions/${version}/partials/${partial}`).then(() => {}),
    getPartialChildren: async (version: string, partial: string) => {
      const response = await api.get<PartialTemplate[]>(`/api/v1/versions/${version}/partials/${partial}/children`);
      return response.data;
    },
  };
} 