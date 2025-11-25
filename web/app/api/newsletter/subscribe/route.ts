import { NextRequest, NextResponse } from 'next/server';
import { subscribeToNewsletter } from '@/lib/mailerlite';
import { getPostHogClient } from '@/lib/posthog-server';

export async function POST(req: NextRequest) {
  try {
    const { email, name } = await req.json();

    // Validate email format
    if (!email || !email.includes('@')) {
      return NextResponse.json(
        { error: 'Invalid email address' },
        { status: 400 }
      );
    }

    // Subscribe to MailerLite Newsletter group
    const newsletterGroupId = process.env.MAILERLITE_GROUP_NEWSLETTER;

    try {
      await subscribeToNewsletter(
        {
          email,
          ...(name && { name }),
          fields: {
            source: 'website_newsletter',
            signup_date: new Date().toISOString(),
          },
        },
        newsletterGroupId // Add to Newsletter group
      );
    } catch (mailerliteError: any) {
      console.error('MailerLite subscription error:', mailerliteError);

      // Handle duplicate subscriber gracefully
      if (mailerliteError.response?.status === 422) {
        // Email already subscribed - return success
        return NextResponse.json({
          success: true,
          message: 'Already subscribed'
        });
      }

      return NextResponse.json(
        { error: 'Failed to subscribe to newsletter' },
        { status: 500 }
      );
    }

    // Track newsletter subscription in PostHog
    try {
      const posthog = getPostHogClient();
      posthog.capture({
        distinctId: email,
        event: 'newsletter_subscribed',
        properties: {
          email: email,
          source: 'website_newsletter',
        },
      });
      await posthog.shutdown();
    } catch (posthogError) {
      // Log but don't fail the request if PostHog fails
      console.error('PostHog tracking error:', posthogError);
    }

    return NextResponse.json({
      success: true,
      message: 'Successfully subscribed!'
    });
  } catch (error) {
    console.error('Newsletter subscription error:', error);
    return NextResponse.json(
      { error: 'Failed to subscribe' },
      { status: 500 }
    );
  }
}
