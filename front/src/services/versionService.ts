import { useApi } from '@/lib/api';
import { VersionInfo } from '@/types/version';

export class VersionService {
  async getVersions(): Promise<VersionInfo[]> {
    const api = useApi();
    return api.getVersions();
  }

  async getVersion(version: string): Promise<VersionInfo> {
    const api = useApi();
    return api.getVersion(version);
  }

  async createVersion(version: string): Promise<VersionInfo> {
    const api = useApi();
    const response = await api.post('/versions', { version });
    return response.data;
  }

  async updateVersion(oldVersion: string, newVersion: string): Promise<VersionInfo> {
    const api = useApi();
    const response = await api.put(`/versions/${oldVersion}`, { version: newVersion });
    return response.data;
  }

  async deleteVersion(version: string): Promise<void> {
    const api = useApi();
    await api.delete(`/versions/${version}`);
  }
}

export const versionService = new VersionService(); 