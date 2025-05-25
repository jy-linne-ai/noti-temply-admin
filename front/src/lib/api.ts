import axios from 'axios';
import { Version } from '@/types/version';
import { Layout } from '@/types/layout';
import { Template } from '@/types/template';
import { PartialTemplate } from '@/types/partial';

// API URL
export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// API 엔드포인트 (private)
const API_ENDPOINTS = {
  versions: {
    list: '/versions',
    get: (version: string) => `/versions/${version}`,
  },
  layouts: {
    list: (version: string) => `/versions/${version}/layouts`,
    get: (version: string, layout: string) => `/versions/${version}/layouts/${layout}`,
  },
  templates: {
    list: (version: string) => `/versions/${version}/templates`,
    names: (version: string) => `/versions/${version}/template-names`,
    get: (version: string, template: string) => `/versions/${version}/templates/${template}`,
    components: {
      list: (version: string, template: string) => `/versions/${version}/templates/${template}/components`,
      get: (version: string, template: string, component: string) => 
        `/versions/${version}/templates/${template}/components/${component}`,
    }
  },
  partials: {
    list: (version: string) => `/versions/${version}/partials`,
    get: (version: string, partial: string) => `/versions/${version}/partials/${partial}`,
    children: (version: string, partial: string) => 
      `/versions/${version}/partials/${partial}/children`,
    parents: (version: string, partial: string) => 
      `/versions/${version}/partials/${partial}/parents`,
  },
} as const;

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 요청 시작 시간을 저장할 Map
const requestStartTimes = new Map<string, number>();

// 요청 인터셉터
api.interceptors.request.use(
  (config) => {
    const requestId = `${config.method}-${config.url}`;
    requestStartTimes.set(requestId, Date.now());
    
    console.log('API Request:', {
      method: config.method,
      url: `${config.baseURL}${config.url}`,
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
    const requestId = `${response.config.method}-${response.config.url}`;
    const startTime = requestStartTimes.get(requestId);
    const endTime = Date.now();
    const duration = startTime ? endTime - startTime : 0;
    requestStartTimes.delete(requestId);

    console.log('API Response:', {
      status: response.status,
      url: `${response.config.baseURL}${response.config.url}`,
      data: response.data,
      duration: `${duration}ms`,
    });
    return response;
  },
  (error) => {
    const requestId = error.config ? `${error.config.method}-${error.config.url}` : 'unknown';
    const startTime = requestStartTimes.get(requestId);
    const endTime = Date.now();
    const duration = startTime ? endTime - startTime : 0;
    requestStartTimes.delete(requestId);

    console.error('API Response Error:', {
      status: error.response?.status,
      url: error.config?.baseURL + error.config?.url,
      data: error.response?.data,
      message: error.message,
      duration: `${duration}ms`,
    });
    return Promise.reject(error);
  }
);

// API 응답 처리 헬퍼 함수
const handleResponse = <T>(response: { data: T | { data: T } }): T => {
  if (response.data && typeof response.data === 'object' && 'data' in response.data) {
    return response.data.data;
  }
  return response.data as T;
};

// API 응답 캐시를 위한 Map
const responseCache = new Map<string, {
  data: any;
  timestamp: number;
}>();

// 캐시 유효 시간 (5분)
const CACHE_DURATION = 5 * 60 * 1000;

// 캐시된 API 호출 함수
const cachedApiCall = async <T>(
  key: string,
  apiCall: () => Promise<T>
): Promise<T> => {
  const cached = responseCache.get(key);
  const now = Date.now();

  if (cached && now - cached.timestamp < CACHE_DURATION) {
    console.log('Using cached response for:', key);
    return cached.data;
  }

  const response = await apiCall();
  responseCache.set(key, {
    data: response,
    timestamp: now
  });
  return response;
};

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
  
  // 파셜 관련 API
  getPartials: (version: string, isRoot: boolean) => Promise<PartialTemplate[]>;
  getAllPartials: (version: string) => Promise<PartialTemplate[]>;
  getPartial: (version: string, partial: string) => Promise<PartialTemplate>;
  createPartial: (version: string, data: Partial<PartialTemplate>) => Promise<PartialTemplate>;
  updatePartial: (version: string, partial: string, data: Partial<PartialTemplate>) => Promise<PartialTemplate>;
  deletePartial: (version: string, partial: string) => Promise<void>;
  getPartialChildren: (version: string, partial: string) => Promise<PartialTemplate[]>;

  // 템플릿 관련 API
  getTemplates: (version: string) => Promise<Template[]>;
  getTemplate: (version: string, template: string) => Promise<Template>;
  createTemplate: (version: string, data: Partial<Template>) => Promise<Template>;
  updateTemplate: (version: string, template: string, data: Partial<Template>) => Promise<Template>;
  deleteTemplate: (version: string, template: string) => Promise<void>;
  getTemplateNames: (version: string) => Promise<string[]>;

  // 템플릿 컴포넌트 관련 API
  getAllTemplateComponents: () => Promise<string[]>;
  getTemplateComponents: (version: string, template: string) => Promise<Template[]>;
  getTemplateComponent: (version: string, template: string, component: string) => Promise<Template>;
  updateTemplateComponent: (version: string, template: string, component: string, data: Partial<Template>) => Promise<Template>;
}

export function useApi(): ApiClient {
  return {
    // 버전 관련 API
    getVersions: () => api.get(API_ENDPOINTS.versions.list).then(handleResponse),
    getVersion: (version: string) => api.get(API_ENDPOINTS.versions.get(version)).then(handleResponse),
    createVersion: (version: string) => api.post(API_ENDPOINTS.versions.list, { version }).then(handleResponse),
    updateVersion: (oldVersion: string, newVersion: string) => 
      api.put(API_ENDPOINTS.versions.get(oldVersion), { version: newVersion }).then(handleResponse),
    deleteVersion: (version: string) => api.delete(API_ENDPOINTS.versions.get(version)),
    
    // 레이아웃 관련 API
    getLayouts: (version: string) => api.get(API_ENDPOINTS.layouts.list(version)).then(handleResponse),
    getLayout: (version: string, layout: string) => 
      api.get(API_ENDPOINTS.layouts.get(version, layout)).then(handleResponse),
    createLayout: (version: string, data: Partial<Layout>) => 
      api.post(API_ENDPOINTS.layouts.list(version), data).then(handleResponse),
    updateLayout: (version: string, layout: string, data: Partial<Layout>) => 
      api.put(API_ENDPOINTS.layouts.get(version, layout), data).then(handleResponse),
    deleteLayout: (version: string, layout: string) => 
      api.delete(API_ENDPOINTS.layouts.get(version, layout)),
    
    // 파셜 관련 API
    getPartials: (version: string, isRoot: boolean) => 
      api.get(`${API_ENDPOINTS.partials.list(version)}?is_root=${isRoot}`).then(handleResponse),
    getAllPartials: (version: string) => 
      api.get(API_ENDPOINTS.partials.list(version)).then(handleResponse),
    getPartial: (version: string, partial: string) => 
      api.get(API_ENDPOINTS.partials.get(version, partial)).then(handleResponse),
    createPartial: (version: string, data: Partial<PartialTemplate>) => 
      api.post(API_ENDPOINTS.partials.list(version), data).then(handleResponse),
    updatePartial: (version: string, partial: string, data: Partial<PartialTemplate>) => 
      api.put(API_ENDPOINTS.partials.get(version, partial), data).then(handleResponse),
    deletePartial: (version: string, partial: string) => 
      api.delete(API_ENDPOINTS.partials.get(version, partial)),
    getPartialChildren: (version: string, partial: string) => 
      api.get(API_ENDPOINTS.partials.children(version, partial)).then(handleResponse),

    // 템플릿 관련 API
    getTemplates: (version: string) => api.get(API_ENDPOINTS.templates.list(version)).then(handleResponse),
    getTemplate: (version: string, template: string) => 
      api.get(API_ENDPOINTS.templates.get(version, template)).then(handleResponse),
    createTemplate: (version: string, data: Partial<Template>) => 
      api.post(API_ENDPOINTS.templates.list(version), data).then(handleResponse),
    updateTemplate: (version: string, template: string, data: Partial<Template>) => 
      api.put(API_ENDPOINTS.templates.get(version, template), data).then(handleResponse),
    deleteTemplate: (version: string, template: string) => 
      api.delete(API_ENDPOINTS.templates.get(version, template)),
    getTemplateNames: (version: string) => 
      api.get(API_ENDPOINTS.templates.names(version)).then(handleResponse),

    // 템플릿 컴포넌트 관련 API
    getAllTemplateComponents: () => api.get('/template-components').then(handleResponse),
    getTemplateComponents: (version: string, template: string) => 
      cachedApiCall(
        `template-components-${version}-${template}`,
        () => api.get(API_ENDPOINTS.templates.components.list(version, template)).then(handleResponse)
      ),
    getTemplateComponent: (version: string, template: string, component: string) => 
      cachedApiCall(
        `template-component-${version}-${template}-${component}`,
        () => api.get(API_ENDPOINTS.templates.components.get(version, template, component)).then(handleResponse)
      ),
    updateTemplateComponent: (version: string, template: string, component: string, data: Partial<Template>) => 
      api.put(API_ENDPOINTS.templates.components.get(version, template, component), data).then(handleResponse),
  };
} 