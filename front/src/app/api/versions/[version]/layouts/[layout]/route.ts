import { NextResponse } from "next/server";
import { API_URL } from "@/lib/constants";

export async function GET(
  request: Request,
  { params }: { params: { version: string; layout: string } }
) {
  try {
    const response = await fetch(`${API_URL}/versions/${params.version}/layouts/${params.layout}`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch layout');
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error fetching layout:', error);
    return NextResponse.json(
      { error: 'Failed to fetch layout' },
      { status: 500 }
    );
  }
}

export async function PUT(
  request: Request,
  { params }: { params: { version: string; layout: string } }
) {
  try {
    const body = await request.json();
    const response = await fetch(`${API_URL}/versions/${params.version}/layouts/${params.layout}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      throw new Error('Failed to update layout');
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error updating layout:', error);
    return NextResponse.json(
      { error: 'Failed to update layout' },
      { status: 500 }
    );
  }
}

export async function DELETE(
  request: Request,
  { params }: { params: { version: string; layout: string } }
) {
  try {
    const response = await fetch(`${API_URL}/versions/${params.version}/layouts/${params.layout}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      throw new Error('Failed to delete layout');
    }

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Error deleting layout:', error);
    return NextResponse.json(
      { error: 'Failed to delete layout' },
      { status: 500 }
    );
  }
} 