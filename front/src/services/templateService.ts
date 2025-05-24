import { api } from '@/lib/api';
import { Template, UpdateTemplateRequest } from '@/types/template';

export const templateService = {
  getTemplates: async (version: string): Promise<Template[]> => {
    const response = await api.get<Template[]>(`/api/v1/versions/${version}/templates`);
    return response.data;
  },

  getTemplate: async (version: string, template: string, component: string): Promise<Template> => {
    const response = await api.get<Template>(`/api/v1/versions/${version}/templates/${template}/comports/${component}`);
    return response.data;
  },

  updateTemplate: async (
    version: string,
    template: string,
    component: string,
    data: UpdateTemplateRequest
  ): Promise<Template> => {
    const response = await api.put<Template>(
      `/api/v1/versions/${version}/templates/${template}/comports/${component}`,
      data
    );
    return response.data;
  },
}; 