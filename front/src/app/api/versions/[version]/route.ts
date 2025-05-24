import { NextResponse } from "next/server";
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import { API_URL } from "@/lib/constants";

export async function GET(
  request: Request,
  { params }: { params: { version: string } }
) {
  const response = await fetch(`${API_URL}/versions/${params.version}`);
  const data = await response.json();
  return NextResponse.json(data);
}

export async function DELETE(
  request: Request,
  { params }: { params: { version: string } }
) {
  const response = await fetch(`${API_URL}/versions/${params.version}`, {
    method: 'DELETE',
  });
  return NextResponse.json({ success: true });
} 