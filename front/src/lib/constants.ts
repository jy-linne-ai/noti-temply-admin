export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export const API_ENDPOINTS = {
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
    get: (version: string, template: string) => `/versions/${version}/templates/${template}`,
    items: {
      list: (version: string, template: string) => 
        `/versions/${version}/templates/${template}/items`,
      get: (version: string, template: string, item: string) => 
        `/versions/${version}/templates/${template}/items/${item}`,
    },
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