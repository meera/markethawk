import { betterAuth } from 'better-auth';
import { drizzleAdapter } from 'better-auth/adapters/drizzle';
import { organization } from 'better-auth/plugins/organization';
import { stripe } from '@better-auth/stripe';
import { db } from './db';
import Stripe from 'stripe';

// Initialize Stripe client
const stripeClient = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2024-11-20.acacia',
});

export const auth = betterAuth({
  database: drizzleAdapter(db, {
    provider: 'pg',
  }),
  emailAndPassword: {
    enabled: true,
  },
  socialProviders: {
    google: {
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
      // Enable Google One Tap
      oneTap: true,
    },
    github: {
      clientId: process.env.GITHUB_CLIENT_ID || '',
      clientSecret: process.env.GITHUB_CLIENT_SECRET || '',
      enabled: !!process.env.GITHUB_CLIENT_ID,
    },
  },
  plugins: [
    organization({
      // Automatically creates:
      // - organization table
      // - member table
      // - invitation table
      async sendInvitationEmail(data) {
        // TODO: Implement email sending (Resend)
        console.log('Send invitation email:', data);
      },
      // roles configuration removed temporarily - will be added when better-auth plugin supports it
    }),
    stripe({
      stripeClient,
      // Stripe product configuration
      products: {
        pro: {
          priceId: process.env.STRIPE_PRO_MONTHLY_PRICE_ID!,
          metadata: {
            plan: 'pro',
            billing_period: 'monthly',
          },
        },
        proYearly: {
          priceId: process.env.STRIPE_PRO_YEARLY_PRICE_ID!,
          metadata: {
            plan: 'pro',
            billing_period: 'yearly',
          },
        },
        team: {
          priceId: process.env.STRIPE_TEAM_MONTHLY_PRICE_ID!,
          metadata: {
            plan: 'team',
            billing_period: 'monthly',
          },
        },
        teamYearly: {
          priceId: process.env.STRIPE_TEAM_YEARLY_PRICE_ID!,
          metadata: {
            plan: 'team',
            billing_period: 'yearly',
          },
        },
      },
      // Webhook configuration
      webhookSecret: process.env.STRIPE_WEBHOOK_SECRET!,
      // Success/cancel URLs
      successUrl: process.env.NEXT_PUBLIC_APP_URL + '/billing?success=true',
      cancelUrl: process.env.NEXT_PUBLIC_APP_URL + '/pricing?canceled=true',
    }),
  ],
  trustedOrigins: [
    'http://localhost:3000',
    'https://markethawkeye.com',
    'https://www.markethawkeye.com',
  ],
});

export type Session = typeof auth.$Infer.Session;
export type User = typeof auth.$Infer.Session.user;
