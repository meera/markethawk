import { NextRequest, NextResponse } from 'next/server';
import { db } from '@/lib/db';
import { newsletterSubscribers } from '@/lib/db/schema';

export async function POST(req: NextRequest) {
  try {
    const { email } = await req.json();

    // Validate email format
    if (!email || !email.includes('@')) {
      return NextResponse.json(
        { error: 'Invalid email address' },
        { status: 400 }
      );
    }

    // Store in database (will create table if needed)
    try {
      await db.insert(newsletterSubscribers).values({
        email: email.toLowerCase().trim(),
        subscribedAt: new Date(),
      });
    } catch (error: any) {
      // If email already exists, treat as success (idempotent)
      if (error?.code === '23505') {
        return NextResponse.json({ success: true });
      }
      throw error;
    }

    // TODO: Send confirmation email via Resend when configured
    // await sendConfirmationEmail(email);

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Newsletter subscription error:', error);
    return NextResponse.json(
      { error: 'Failed to subscribe' },
      { status: 500 }
    );
  }
}
