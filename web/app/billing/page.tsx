import { Metadata } from 'next';
import Link from 'next/link';
import { Logo } from '@/components/Logo';
import { auth } from '@/lib/auth';
import { headers } from 'next/headers';
import { redirect } from 'next/navigation';
import { db } from '@/lib/db';
import { sql } from 'drizzle-orm';

export const metadata: Metadata = {
  title: 'Billing - Markey HawkEye',
  description: 'Manage your subscription and billing information',
};

async function getUserSubscription(userId: string) {
  try {
    const result = await db.execute(sql`
      SELECT
        stripe_customer_id,
        stripe_subscription_id,
        stripe_subscription_status,
        stripe_current_period_end,
        stripe_plan_id
      FROM user
      WHERE id = ${userId}
    `);

    return result[0] as any;
  } catch (error) {
    console.error('Failed to fetch subscription:', error);
    return null;
  }
}

export default async function BillingPage({
  searchParams,
}: {
  searchParams: Promise<{ success?: string; canceled?: string }>;
}) {
  const session = await auth.api.getSession({
    headers: await headers(),
  });

  if (!session) {
    redirect('/api/auth/google-one-tap');
  }

  const subscription = await getUserSubscription(session.user.id);
  const params = await searchParams;

  // Determine plan name from stripe_plan_id
  const getPlanName = (planId?: string) => {
    if (!planId) return 'Free';
    if (planId.includes('pro')) return 'Pro';
    if (planId.includes('team')) return 'Team';
    return 'Free';
  };

  const planName = getPlanName(subscription?.stripe_plan_id);
  const isActive = subscription?.stripe_subscription_status === 'active';
  const isCanceled = subscription?.stripe_subscription_status === 'canceled';

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background-elevated to-background">
      {/* Header */}
      <header className="border-b border-border backdrop-blur-sm bg-background/80 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <Logo />

            <nav className="flex items-center space-x-6">
              <Link href="/" className="text-text-tertiary hover:text-primary transition-colors text-sm">
                Companies
              </Link>
              <Link href="/pricing" className="text-text-tertiary hover:text-primary transition-colors text-sm">
                Pricing
              </Link>
              <Link href="/billing" className="text-primary font-medium transition-colors text-sm">
                Billing
              </Link>
            </nav>
          </div>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Success/Cancel Messages */}
        {params.success && (
          <div className="mb-8 bg-green-500/10 border border-green-500/20 rounded-xl p-4">
            <div className="flex items-center gap-3">
              <svg className="w-6 h-6 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              <p className="text-green-500 font-semibold">
                Subscription activated! Welcome to Markey HawkEye {planName}.
              </p>
            </div>
          </div>
        )}

        {params.canceled && (
          <div className="mb-8 bg-yellow-500/10 border border-yellow-500/20 rounded-xl p-4">
            <div className="flex items-center gap-3">
              <svg className="w-6 h-6 text-yellow-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <p className="text-yellow-500 font-semibold">
                Checkout canceled. No worries, you can try again anytime.
              </p>
            </div>
          </div>
        )}

        {/* Page Title */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-text-primary mb-2">Billing & Subscription</h1>
          <p className="text-xl text-text-secondary">
            Manage your subscription and billing information
          </p>
        </div>

        {/* Current Plan Card */}
        <div className="bg-background-muted/40 border border-border rounded-2xl p-8 mb-8">
          <div className="flex items-start justify-between mb-6">
            <div>
              <h2 className="text-2xl font-bold text-text-primary mb-2">Current Plan</h2>
              <p className="text-text-secondary">
                You are currently on the <span className="font-semibold text-primary">{planName}</span> plan
              </p>
            </div>
            {isActive && (
              <span className="px-3 py-1 bg-green-500/10 text-green-500 rounded-full text-sm font-semibold">
                Active
              </span>
            )}
            {isCanceled && (
              <span className="px-3 py-1 bg-red-500/10 text-red-500 rounded-full text-sm font-semibold">
                Canceled
              </span>
            )}
          </div>

          {subscription?.stripe_current_period_end && (
            <div className="mb-6 pb-6 border-b border-border">
              <p className="text-text-tertiary text-sm">
                {isActive ? 'Next billing date:' : 'Access until:'}{' '}
                <span className="font-semibold text-text-secondary">
                  {new Date(subscription.stripe_current_period_end).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                  })}
                </span>
              </p>
            </div>
          )}

          <div className="flex gap-4">
            {planName === 'Free' ? (
              <Link
                href="/pricing"
                className="px-6 py-3 bg-primary hover:bg-primary-dark text-white rounded-lg font-semibold transition-all"
              >
                Upgrade to Pro
              </Link>
            ) : (
              <Link
                href="/api/billing/portal"
                className="px-6 py-3 bg-primary hover:bg-primary-dark text-white rounded-lg font-semibold transition-all"
              >
                Manage Subscription
              </Link>
            )}
            <Link
              href="/pricing"
              className="px-6 py-3 bg-background-elevated hover:bg-background-muted border border-border text-primary rounded-lg font-semibold transition-all"
            >
              View All Plans
            </Link>
          </div>
        </div>

        {/* Usage Stats (if applicable) */}
        {planName === 'Free' && (
          <div className="bg-background-muted/40 border border-border rounded-2xl p-8 mb-8">
            <h2 className="text-xl font-bold text-text-primary mb-4">Usage This Month</h2>
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <p className="text-text-tertiary text-sm mb-2">Video Views</p>
                <div className="flex items-baseline gap-2">
                  <span className="text-3xl font-bold text-text-primary">0</span>
                  <span className="text-text-tertiary">/ 3</span>
                </div>
                <div className="mt-2 h-2 bg-background-elevated rounded-full overflow-hidden">
                  <div className="h-full bg-primary" style={{ width: '0%' }} />
                </div>
              </div>
              <div>
                <p className="text-text-tertiary text-sm mb-2">Companies Accessed</p>
                <div className="flex items-baseline gap-2">
                  <span className="text-3xl font-bold text-text-primary">0</span>
                  <span className="text-text-tertiary">/ 100</span>
                </div>
              </div>
            </div>
            <div className="mt-6 p-4 bg-primary/10 rounded-lg">
              <p className="text-sm text-text-secondary">
                Upgrade to Pro for unlimited access to all 7,372 companies
              </p>
            </div>
          </div>
        )}

        {/* Benefits */}
        <div className="bg-background-muted/40 border border-border rounded-2xl p-8">
          <h2 className="text-xl font-bold text-text-primary mb-6">Your Benefits</h2>
          <ul className="space-y-3">
            {planName === 'Free' ? (
              <>
                <li className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span className="text-text-secondary">3 video views per month</span>
                </li>
                <li className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span className="text-text-secondary">Access to top 100 companies</span>
                </li>
                <li className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span className="text-text-secondary">480p video quality</span>
                </li>
              </>
            ) : planName === 'Pro' ? (
              <>
                <li className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span className="text-text-secondary">Unlimited video views</span>
                </li>
                <li className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span className="text-text-secondary">All 7,372 companies</span>
                </li>
                <li className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span className="text-text-secondary">1080p HD video quality</span>
                </li>
                <li className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span className="text-text-secondary">Download transcripts</span>
                </li>
                <li className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span className="text-text-secondary">Email alerts for new earnings</span>
                </li>
              </>
            ) : (
              <>
                <li className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span className="text-text-secondary">Everything in Pro</span>
                </li>
                <li className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span className="text-text-secondary">5 team members</span>
                </li>
                <li className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span className="text-text-secondary">API access (coming soon)</span>
                </li>
                <li className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span className="text-text-secondary">Dedicated support</span>
                </li>
              </>
            )}
          </ul>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-border mt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
            <div className="flex items-center space-x-3">
              <Logo size="small" />
              <span className="text-text-tertiary text-sm">
                © 2024 Markey HawkEye. Transform earnings calls into visual insights.
              </span>
            </div>

            <div className="flex items-center space-x-6 text-sm">
              <Link href="mailto:thehawkeyemarket@gmail.com" className="text-text-tertiary hover:text-accent transition-colors">
                Contact
              </Link>
              <Link href="/about" className="text-text-tertiary hover:text-accent transition-colors">
                About
              </Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
