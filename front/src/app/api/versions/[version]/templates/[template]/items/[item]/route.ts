import { NextResponse } from "next/server";
import { api } from "@/services/apiClient";

export async function GET(
  request: Request,
  { params }: { params: { version: string; template: string; item: string } }
) {
  try {
    const response = await api.templates.getItem(params.version, params.template, params.item);
    return NextResponse.json(response.data);
  } catch (error) {
    console.error('Error fetching template item:', error);
    return NextResponse.json(
      { error: 'Failed to fetch template item' },
      { status: 500 }
    );
  }
}

export async function PUT(
  request: Request,
  { params }: { params: { version: string; template: string; item: string } }
) {
  try {
    const body = await request.json();
    const response = await api.templates.updateItem(params.version, params.template, params.item, body);
    return NextResponse.json(response.data);
  } catch (error) {
    console.error('Error updating template item:', error);
    return NextResponse.json(
      { error: 'Failed to update template item' },
      { status: 500 }
    );
  }
}

export async function DELETE(
  request: Request,
  { params }: { params: { version: string; template: string; item: string } }
) {
  try {
    await api.templates.deleteItem(params.version, params.template, params.item);
    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Error deleting template item:', error);
    return NextResponse.json(
      { error: 'Failed to delete template item' },
      { status: 500 }
    );
  }
} 