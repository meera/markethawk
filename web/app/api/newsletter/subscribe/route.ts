import { NextRequest, NextResponse } from 'next/server';
import { sendNewSubscriberNotification } from '@/lib/email';
import { getPostHogClient } from '@/lib/posthog-server';

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

    // Send email notification to admin
    try {
      await sendNewSubscriberNotification(email);
    } catch (emailError) {
      console.error('Failed to send notification email:', emailError);
      return NextResponse.json(
        { error: 'Failed to send notification' },
        { status: 500 }
      );
    }

    // Track newsletter subscription in PostHog
    const posthog = getPostHogClient();
    posthog.capture({
      distinctId: email,
      event: 'newsletter_subscribed',
      properties: {
        email: email,
      },
    });
    await posthog.shutdown();

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Newsletter subscription error:', error);
    return NextResponse.json(
      { error: 'Failed to subscribe' },
      { status: 500 }
    );
  }
}
