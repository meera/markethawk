'use client';

import Link from 'next/link';
import posthog from 'posthog-js';

export default function PricingPage() {
  const handleUpgradeClick = (planName: string, planPrice: string) => {
    posthog.capture('upgrade_clicked', {
      plan_name: planName,
      plan_price: planPrice,
    });
  };

  const plans = [
    {
      name: 'Explorer',
      price: '$0',
      period: '',
      tagline: 'Test the waters',
      features: [
        'Screen 7,372 companies',
        'Track earnings calendars',
        'Preview transcript excerpts',
        'Basic company data',
        'Community access',
      ],
      cta: 'Start Free',
      href: '/auth/signin',
      highlighted: false,
    },
    {
      name: 'Professional',
      price: '$39',
      period: '/month',
      tagline: 'Full market intelligence',
      features: [
        'Complete earnings call access',
        'Institutional-grade transcripts',
        'AI-powered signal detection',
        'Sentiment shifts & insider tone analysis',
        'Export capabilities',
        'Real-time alerts',
        'Priority support',
        'Month-to-month',
      ],
      cta: 'Get Access',
      href: 'https://buy.stripe.com/9B65kCbaj0vc0CJbUu6AM00',
      highlighted: true,
      external: true,
    },
    {
      name: 'Institution',
      price: '$297',
      period: '/month',
      tagline: 'Elite trader arsenal',
      features: [
        'Everything in Professional',
        'API access for custom tools',
        'Bulk transcript exports',
        'White-label charts for content',
        '10-user team seats',
        'Custom alert parameters',
        'Dedicated success manager',
        'Early access to new features',
        'Quarterly strategy calls',
      ],
      cta: 'Contact Sales',
      href: 'mailto:thehawkeyemarket@gmail.com?subject=Institution%20Plan%20Inquiry',
      highlighted: false,
      external: true,
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background-elevated to-background">
      {/* Header */}
      <header className="border-b border-border bg-background/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="text-xl font-bold text-primary">
              MarketHawk
            </Link>
            <nav className="flex items-center space-x-6">
              <Link href="/" className="text-text-tertiary hover:text-primary transition-colors text-sm">
                Companies
              </Link>
              <Link href="/pricing" className="text-primary font-medium transition-colors text-sm">
                Pricing
              </Link>
            </nav>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
        {/* Hero */}
        <div className="text-center mb-16">
          <h1 className="text-4xl md:text-5xl font-bold text-text-primary mb-4">
            Get The Same Earnings Intelligence Hedge Funds Pay $30K For
          </h1>
          <p className="text-xl text-text-secondary max-w-2xl mx-auto">
            Your edge in the market starts here.
          </p>
        </div>

        {/* Pricing Cards */}
        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {plans.map((plan) => (
            <div
              key={plan.name}
              className={`relative rounded-2xl border-2 p-8 flex flex-col ${
                plan.highlighted
                  ? 'border-primary bg-primary/5 shadow-xl shadow-primary/20'
                  : 'border-border bg-background-elevated'
              }`}
            >
              {plan.highlighted && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2 px-4 py-1 bg-primary text-white text-sm font-medium rounded-full">
                  Most Popular
                </div>
              )}

              <div className="text-center mb-8">
                <h3 className="text-2xl font-bold text-text-primary mb-2">
                  {plan.name}
                </h3>
                <div className="mb-4">
                  <span className="text-5xl font-bold text-text-primary">
                    {plan.price}
                  </span>
                  {plan.period && (
                    <span className="text-text-secondary text-lg">
                      {plan.period}
                    </span>
                  )}
                </div>
                <p className="text-text-secondary font-medium">{plan.tagline}</p>
              </div>

              <ul className="space-y-4 mb-8 flex-grow">
                {plan.features.map((feature, index) => (
                  <li key={index} className="flex items-start">
                    <svg
                      className="h-6 w-6 text-primary flex-shrink-0"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M5 13l4 4L19 7"
                      />
                    </svg>
                    <span className="ml-3 text-text-secondary">{feature}</span>
                  </li>
                ))}
              </ul>

              <Link
                href={plan.href}
                target={plan.external ? '_blank' : undefined}
                rel={plan.external ? 'noopener noreferrer' : undefined}
                onClick={() => handleUpgradeClick(plan.name, plan.price)}
                className={`block w-full py-3 px-6 rounded-lg text-center font-medium transition-all ${
                  plan.highlighted
                    ? 'bg-primary text-white hover:bg-primary-hover shadow-lg hover:shadow-xl'
                    : 'bg-background-muted text-text-primary hover:bg-border'
                }`}
              >
                {plan.cta}
              </Link>
            </div>
          ))}
        </div>

        {/* Contact Info */}
        <div className="mt-16 text-center">
          <p className="text-text-secondary">
            Questions? Email us at{' '}
            <a
              href="mailto:thehawkeyemarket@gmail.com"
              className="text-primary hover:underline"
            >
              thehawkeyemarket@gmail.com
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}
