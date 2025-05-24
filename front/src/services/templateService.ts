import { useApi } from '@/lib/api';
import { Template } from '@/types/template';

export const templateService = {
  getTemplates: async (version: string, layout: string) => {
    const api = useApi();
    return api.getTemplates(version, layout);
  },
  getTemplate: async (version: string, layout: string, template: string) => {
    const api = useApi();
    return api.getTemplate(version, layout, template);
  },
}; 