import { NextResponse } from "next/server";
import { API_URL } from "@/lib/constants";

export async function GET() {
  try {
    const response = await fetch(`${API_URL}/versions`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch versions');
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error fetching versions:', error);
    return NextResponse.json(
      { error: 'Failed to fetch versions' },
      { status: 500 }
    );
  }
}

export async function POST(request: Request) {
  const body = await request.json();
  const response = await fetch(`${API_URL}/versions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  });
  const data = await response.json();
  return NextResponse.json(data);
} 