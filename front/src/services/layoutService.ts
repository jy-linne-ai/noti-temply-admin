import { useApi } from '@/lib/api';
import { Layout } from '@/types/layout';

export const layoutService = {
  getLayouts: async (version: string): Promise<Layout[]> => {
    const api = useApi();
    return api.getLayouts(version);
  },
  getLayout: async (version: string, layoutName: string): Promise<Layout> => {
    const api = useApi();
    return api.getLayout(version, layoutName);
  },
  createLayout: async (version: string, data: Partial<Layout>): Promise<Layout> => {
    const api = useApi();
    const response = await api.post(`/versions/${version}/layouts`, data);
    return response.data;
  },
  updateLayout: async (version: string, layoutName: string, data: Partial<Layout>): Promise<Layout> => {
    const api = useApi();
    const response = await api.put(`/versions/${version}/layouts/${layoutName}`, data);
    return response.data;
  },
  deleteLayout: async (version: string, layoutName: string): Promise<void> => {
    const api = useApi();
    await api.delete(`/versions/${version}/layouts/${layoutName}`);
  },
}; 