import { betterAuth } from 'better-auth';
import { drizzleAdapter } from 'better-auth/adapters/drizzle';
import { organization } from 'better-auth/plugins/organization';
import { db } from './db';

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
  ],
  trustedOrigins: [
    'http://localhost:3000',
    'https://earninglens.com',
    'https://www.earninglens.com',
  ],
});

export type Session = typeof auth.$Infer.Session;
export type User = typeof auth.$Infer.Session.user;
