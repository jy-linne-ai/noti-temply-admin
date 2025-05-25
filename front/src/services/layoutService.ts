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
    const response = await api.createLayout(version, data);
    return response.data;
  },
  updateLayout: async (version: string, layoutName: string, data: Partial<Layout>): Promise<Layout> => {
    const api = useApi();
    const response = await api.updateLayout(version, layoutName, data);
    return response.data;
  },
  deleteLayout: async (version: string, layoutName: string): Promise<void> => {
    const api = useApi();
    await api.deleteLayout(version, layoutName);
  },
}; 