'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { Version } from '@/types/version';

export default function VersionManagementPage() {
  const [versions, setVersions] = useState<Version[]>([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    fetchVersions();
  }, []);

  const fetchVersions = async () => {
    try {
      const response = await api.get('/api/v1/versions');
      setVersions(response.data);
    } catch (error) {
      console.error('Failed to fetch versions:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateVersion = async () => {
    const version = prompt('새로운 버전을 입력하세요:');
    if (!version) return;

    try {
      await api.post('/api/v1/versions', { version });
      await fetchVersions();
    } catch (error) {
      console.error('Failed to create version:', error);
      alert('버전 생성에 실패했습니다.');
    }
  };

  const handleDeleteVersion = async (version: string) => {
    if (!confirm(`정말로 ${version} 버전을 삭제하시겠습니까?`)) return;

    try {
      await api.delete(`/api/v1/versions/${version}`);
      await fetchVersions();
    } catch (error) {
      console.error('Failed to delete version:', error);
      alert('버전 삭제에 실패했습니다.');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">버전 관리</h1>
        <button
          onClick={handleCreateVersion}
          className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
        >
          새 버전 생성
        </button>
      </div>

      <div className="bg-white shadow-md rounded-lg overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                버전
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                생성일
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                작업
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {versions.map((version) => (
              <tr key={version.version}>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {version.version}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {new Date(version.created_at).toLocaleString()}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  <button
                    onClick={() => handleDeleteVersion(version.version)}
                    className="text-red-600 hover:text-red-900"
                  >
                    삭제
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
} 