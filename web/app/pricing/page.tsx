import { Metadata } from 'next';
import Link from 'next/link';
import { Logo } from '@/components/Logo';
import { auth } from '@/lib/auth';
import { headers } from 'next/headers';
import { redirect } from 'next/navigation';

export const metadata: Metadata = {
  title: 'Pricing - Markey HawkEye',
  description: 'Simple, transparent pricing for earnings call video access. Start free, upgrade anytime.',
};

const plans = [
  {
    name: 'Free',
    price: '$0',
    period: 'forever',
    description: 'Perfect for trying out our platform',
    features: [
      '3 video views per month',
      'Access to top 100 companies',
      'Basic company search',
      '480p video quality',
      'Community support',
    ],
    cta: 'Get Started',
    href: '/api/auth/google-one-tap',
    highlighted: false,
  },
  {
    name: 'Pro',
    price: '$19',
    period: 'per month',
    yearlyPrice: '$190',
    yearlyPeriod: 'per year',
    savings: 'Save 17%',
    description: 'For serious investors and analysts',
    features: [
      'Unlimited video views',
      'All 7,372 companies',
      '1080p HD video quality',
      'Download transcripts',
      'Email alerts for new earnings',
      'Priority support',
    ],
    cta: 'Start Pro Trial',
    href: '/api/billing/checkout?plan=pro',
    highlighted: true,
  },
  {
    name: 'Team',
    price: '$49',
    period: 'per month',
    yearlyPrice: '$490',
    yearlyPeriod: 'per year',
    savings: 'Save 17%',
    description: 'For investment firms and teams',
    features: [
      'Everything in Pro',
      '5 team members',
      'API access (coming soon)',
      'Custom integrations',
      'Dedicated support',
      'White-label options',
    ],
    cta: 'Start Team Trial',
    href: '/api/billing/checkout?plan=team',
    highlighted: false,
  },
];

export default async function PricingPage() {
  const session = await auth.api.getSession({
    headers: await headers(),
  });

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
              <Link href="/pricing" className="text-primary font-medium transition-colors text-sm">
                Pricing
              </Link>
              {session ? (
                <Link
                  href="/billing"
                  className="px-4 py-2 bg-primary hover:bg-primary-dark text-white rounded-lg font-semibold transition-all text-sm"
                >
                  Dashboard
                </Link>
              ) : (
                <Link
                  href="/api/auth/google-one-tap"
                  className="px-4 py-2 bg-primary hover:bg-primary-dark text-white rounded-lg font-semibold transition-all text-sm"
                >
                  Sign In
                </Link>
              )}
            </nav>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        {/* Page Title */}
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-text-primary mb-4">
            Simple, Transparent Pricing
          </h1>
          <p className="text-xl text-text-secondary max-w-2xl mx-auto">
            Start free, upgrade when you need more. No hidden fees, cancel anytime.
          </p>
        </div>

        {/* Pricing Cards */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          {plans.map((plan) => (
            <div
              key={plan.name}
              className={`rounded-2xl p-8 ${
                plan.highlighted
                  ? 'bg-gradient-to-br from-primary/10 to-primary/5 border-2 border-primary shadow-xl shadow-primary/20'
                  : 'bg-background-muted/40 border border-border'
              } relative`}
            >
              {plan.highlighted && (
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                  <span className="bg-primary text-white px-4 py-1 rounded-full text-sm font-semibold">
                    Most Popular
                  </span>
                </div>
              )}

              <div className="mb-6">
                <h3 className="text-2xl font-bold text-text-primary mb-2">{plan.name}</h3>
                <p className="text-text-tertiary text-sm">{plan.description}</p>
              </div>

              <div className="mb-6">
                <div className="flex items-baseline gap-2">
                  <span className="text-5xl font-bold text-text-primary">{plan.price}</span>
                  <span className="text-text-tertiary">{plan.period}</span>
                </div>
                {plan.yearlyPrice && (
                  <div className="mt-2 flex items-baseline gap-2">
                    <span className="text-2xl font-semibold text-text-secondary">{plan.yearlyPrice}</span>
                    <span className="text-text-tertiary text-sm">{plan.yearlyPeriod}</span>
                    <span className="text-primary text-sm font-semibold">{plan.savings}</span>
                  </div>
                )}
              </div>

              <ul className="space-y-3 mb-8">
                {plan.features.map((feature) => (
                  <li key={feature} className="flex items-start gap-3">
                    <svg
                      className="w-5 h-5 text-primary flex-shrink-0 mt-0.5"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    <span className="text-text-secondary text-sm">{feature}</span>
                  </li>
                ))}
              </ul>

              <Link
                href={plan.href}
                className={`block text-center px-6 py-3 rounded-lg font-semibold transition-all ${
                  plan.highlighted
                    ? 'bg-primary hover:bg-primary-dark text-white shadow-lg shadow-primary/20'
                    : 'bg-background-elevated hover:bg-background-muted border border-border text-primary'
                }`}
              >
                {plan.cta}
              </Link>
            </div>
          ))}
        </div>

        {/* FAQ Section */}
        <div className="max-w-3xl mx-auto">
          <h2 className="text-3xl font-bold text-text-primary mb-8 text-center">
            Frequently Asked Questions
          </h2>

          <div className="space-y-6">
            <div className="bg-background-muted/40 border border-border rounded-xl p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-2">
                Can I switch plans anytime?
              </h3>
              <p className="text-text-secondary">
                Yes! Upgrade or downgrade your plan at any time. Changes take effect immediately, and we'll
                prorate any unused time.
              </p>
            </div>

            <div className="bg-background-muted/40 border border-border rounded-xl p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-2">
                What payment methods do you accept?
              </h3>
              <p className="text-text-secondary">
                We accept all major credit cards (Visa, Mastercard, American Express, Discover) through Stripe.
              </p>
            </div>

            <div className="bg-background-muted/40 border border-border rounded-xl p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-2">
                Is there a free trial for paid plans?
              </h3>
              <p className="text-text-secondary">
                Yes! All paid plans come with a 7-day free trial. No credit card required to start.
              </p>
            </div>

            <div className="bg-background-muted/40 border border-border rounded-xl p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-2">
                Do you offer refunds?
              </h3>
              <p className="text-text-secondary">
                Yes! We offer a 30-day money-back guarantee. If you're not satisfied, we'll refund your
                subscription, no questions asked.
              </p>
            </div>
          </div>
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
