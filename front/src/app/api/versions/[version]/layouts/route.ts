import { useApi } from '@/lib/api';

export async function GET(
  request: Request,
  { params }: { params: { version: string } }
) {
  const api = useApi();
  const layouts = await api.getLayouts(params.version);
  return Response.json(layouts);
}

export async function POST(
  request: Request,
  { params }: { params: { version: string } }
) {
  const api = useApi();
  const data = await request.json();
  const layout = await api.createLayout(params.version, data);
  return Response.json(layout);
} 