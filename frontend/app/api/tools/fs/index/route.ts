import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const { path, max_depth = 2 } = await request.json();

    // Forward to backend
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';

    const response = await fetch(`${backendUrl}/tools/fs/index`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ path, max_depth }),
    });

    if (!response.ok) {
      throw new Error('Backend request failed');
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Tools API error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}