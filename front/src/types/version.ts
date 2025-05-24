export interface Version {
  version: string;
  description?: string;
  is_root?: boolean;
  created_at: string;
  updated_at: string;
}

export type VersionList = Version[];

export interface ApiResponse<T> {
  data: T;
  message?: string;
} 