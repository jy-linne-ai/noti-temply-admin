import { api } from '@/lib/api';
import { Template, UpdateTemplateRequest } from '@/types/template';

interface Layout {
  name: string;
  description?: string;
  created_at?: string;
  created_by?: string;
  updated_at?: string;
  updated_by?: string;
  content?: string;
}

export const templateService = {
  getTemplates: async (version: string): Promise<Template[]> => {
    const response = await api.get<Template[]>(`/api/v1/versions/${version}/templates`);
    return response.data;
  },

  getTemplateNames: async (version: string): Promise<string[]> => {
    const response = await api.get<string[]>(`/api/v1/versions/${version}/template-names`);
    return response.data;
  },

  getTemplateComponents: async (version: string, template: string): Promise<Template[]> => {
    const encodedTemplate = encodeURIComponent(template);
    const response = await api.get<Template[]>(`/api/v1/versions/${version}/templates/${encodedTemplate}/components`);
    return response.data;
  },

  getTemplateComponent: async (version: string, template: string, component: string): Promise<Template> => {
    const encodedTemplate = encodeURIComponent(template);
    const response = await api.get<Template>(`/api/v1/versions/${version}/templates/${encodedTemplate}/components/${component}`);
    return response.data;
  },

  getAllTemplateComponents: async (): Promise<string[]> => {
    const response = await api.get<string[]>(`/api/v1/template-components`);
    return response.data;
  },

  updateTemplateComponent: async (
    version: string,
    template: string,
    component: string,
    data: UpdateTemplateRequest
  ): Promise<Template> => {
    const encodedTemplate = encodeURIComponent(template);
    const response = await api.put<Template>(
      `/api/v1/versions/${version}/templates/${encodedTemplate}/components/${component}`,
      data
    );
    return response.data;
  },

  // 레이아웃 관련 메서드
  getLayouts: async (version: string): Promise<Layout[]> => {
    const response = await api.get<Layout[]>(`/api/v1/versions/${version}/layouts`);
    return response.data;
  },

  getLayoutComponents: async (version: string, layout: string): Promise<Template[]> => {
    const response = await api.get<Template[]>(`/api/v1/versions/${version}/layouts/${layout}/components`);
    return response.data;
  },
}; 