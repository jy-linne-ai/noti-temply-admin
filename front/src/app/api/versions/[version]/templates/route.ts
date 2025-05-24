import { useApi } from '@/lib/api';

export async function GET(
  request: Request,
  { params }: { params: { version: string } }
) {
  const api = useApi();
  const searchParams = new URL(request.url).searchParams;
  const layout = searchParams.get('layout');
  
  if (!layout) {
    return Response.json({ error: 'Layout parameter is required' }, { status: 400 });
  }

  const templates = await api.getTemplates(params.version, layout);
  return Response.json(templates);
}

export async function POST(
  request: Request,
  { params }: { params: { version: string } }
) {
  const api = useApi();
  const searchParams = new URL(request.url).searchParams;
  const layout = searchParams.get('layout');
  
  if (!layout) {
    return Response.json({ error: 'Layout parameter is required' }, { status: 400 });
  }

  const data = await request.json();
  const template = await api.createTemplate(params.version, layout, data);
  return Response.json(template);
} 