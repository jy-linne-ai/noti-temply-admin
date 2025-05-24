import { NextResponse } from "next/server";
import { api } from "@/services/apiClient";

export async function GET(
  request: Request,
  { params }: { params: { version: string; template: string } }
) {
  try {
    const response = await api.templates.listItems(params.version, params.template);
    return NextResponse.json(response.data);
  } catch (error) {
    console.error('Error fetching template items:', error);
    return NextResponse.json(
      { error: 'Failed to fetch template items' },
      { status: 500 }
    );
  }
}

export async function POST(
  request: Request,
  { params }: { params: { version: string; template: string } }
) {
  try {
    const body = await request.json();
    const response = await api.templates.createItem(params.version, params.template, body);
    return NextResponse.json(response.data);
  } catch (error) {
    console.error('Error creating template item:', error);
    return NextResponse.json(
      { error: 'Failed to create template item' },
      { status: 500 }
    );
  }
} 