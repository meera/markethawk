#!/usr/bin/env tsx
/**
 * Delete User Script
 *
 * Safely delete a user and all related data from the database.
 * Handles cascade deletions for Better Auth tables and MarketHawk data.
 *
 * Usage:
 *   # Development database (.env.local)
 *   npm run delete-user -- user@example.com
 *   npm run delete-user -- --email user@example.com
 *   npm run delete-user -- --id usr_abc123
 *
 *   # Production database (.env.production)
 *   DEV_MODE=false npm run delete-user -- user@example.com
 *
 * What gets deleted:
 * - User record
 * - Sessions (cascade)
 * - Accounts (cascade)
 * - Organization memberships (cascade)
 * - Invitations sent by user (cascade)
 * - Video views (if userId is set)
 * - Video engagement (if userId is set)
 * - Click throughs (if userId is set)
 */

import { drizzle } from 'drizzle-orm/postgres-js';
import postgres from 'postgres';
import { eq } from 'drizzle-orm';
import * as schema from '../lib/db/schema';
import { user, session, account, member, invitation } from '../lib/db/auth-schema';
import dotenv from 'dotenv';
import { resolve } from 'path';

// Load environment variables based on DEV_MODE
const isDev = process.env.DEV_MODE !== 'false';
const envFile = isDev ? '.env.local' : '.env.production';
const envPath = resolve(process.cwd(), envFile);

console.log(`Loading environment from: ${envFile}`);
dotenv.config({ path: envPath });

// Connect to database
const DATABASE_URL = process.env.DATABASE_URL;
if (!DATABASE_URL) {
  console.error(`❌ DATABASE_URL not found in ${envFile}`);
  process.exit(1);
}

const sql = postgres(DATABASE_URL);
const db = drizzle(sql, { schema });

interface DeleteStats {
  user: number;
  sessions: number;
  accounts: number;
  members: number;
  invitations: number;
  videoViews: number;
  videoEngagement: number;
  clickThroughs: number;
}

async function deleteUser(identifier: string, isEmail: boolean = true): Promise<void> {
  const stats: DeleteStats = {
    user: 0,
    sessions: 0,
    accounts: 0,
    members: 0,
    invitations: 0,
    videoViews: 0,
    videoEngagement: 0,
    clickThroughs: 0,
  };

  try {
    // Find the user
    let foundUser;
    if (isEmail) {
      foundUser = await db.select().from(user).where(eq(user.email, identifier)).limit(1);
    } else {
      foundUser = await db.select().from(user).where(eq(user.id, identifier)).limit(1);
    }

    if (!foundUser || foundUser.length === 0) {
      console.error(`❌ User not found: ${identifier}`);
      process.exit(1);
    }

    const userData = foundUser[0];
    const userId = userData.id;

    console.log('\n📋 User found:');
    console.log(`   ID: ${userData.id}`);
    console.log(`   Email: ${userData.email}`);
    console.log(`   Name: ${userData.name || 'N/A'}`);
    console.log(`   Created: ${userData.createdAt}`);

    // Confirm deletion
    console.log('\n⚠️  This will delete:');
    console.log('   - User account');
    console.log('   - All sessions (cascade)');
    console.log('   - All linked accounts (cascade)');
    console.log('   - Organization memberships (cascade)');
    console.log('   - Invitations sent (cascade)');
    console.log('   - Video views and engagement data');

    // In non-interactive mode, proceed directly
    console.log('\n🗑️  Deleting user data...\n');

    // 1. Delete MarketHawk data (manual cleanup - no cascade)

    // Delete video views
    const deletedViews = await db
      .delete(schema.videoViews)
      .where(eq(schema.videoViews.userId, userId));
    stats.videoViews = deletedViews.rowCount || 0;
    console.log(`✓ Deleted ${stats.videoViews} video views`);

    // Delete video engagement
    const deletedEngagement = await db
      .delete(schema.videoEngagement)
      .where(eq(schema.videoEngagement.userId, userId));
    stats.videoEngagement = deletedEngagement.rowCount || 0;
    console.log(`✓ Deleted ${stats.videoEngagement} video engagement records`);

    // Delete click throughs
    const deletedClicks = await db
      .delete(schema.clickThroughs)
      .where(eq(schema.clickThroughs.userId, userId));
    stats.clickThroughs = deletedClicks.rowCount || 0;
    console.log(`✓ Deleted ${stats.clickThroughs} click throughs`);

    // 2. Count Better Auth related records (will be cascade deleted)

    const sessionCount = await db.select().from(session).where(eq(session.userId, userId));
    stats.sessions = sessionCount.length;

    const accountCount = await db.select().from(account).where(eq(account.userId, userId));
    stats.accounts = accountCount.length;

    const memberCount = await db.select().from(member).where(eq(member.userId, userId));
    stats.members = memberCount.length;

    const invitationCount = await db.select().from(invitation).where(eq(invitation.inviterId, userId));
    stats.invitations = invitationCount.length;

    // 3. Delete the user (cascades to sessions, accounts, members, invitations)
    const deletedUser = await db.delete(user).where(eq(user.id, userId));
    stats.user = deletedUser.rowCount || 0;

    // Print summary
    console.log('\n✅ User deleted successfully!\n');
    console.log('📊 Deletion summary:');
    console.log(`   Users: ${stats.user}`);
    console.log(`   Sessions: ${stats.sessions} (cascade)`);
    console.log(`   Accounts: ${stats.accounts} (cascade)`);
    console.log(`   Org memberships: ${stats.members} (cascade)`);
    console.log(`   Invitations: ${stats.invitations} (cascade)`);
    console.log(`   Video views: ${stats.videoViews}`);
    console.log(`   Video engagement: ${stats.videoEngagement}`);
    console.log(`   Click throughs: ${stats.clickThroughs}`);
    console.log(`   Total records: ${Object.values(stats).reduce((a, b) => a + b, 0)}`);

  } catch (error) {
    console.error('\n❌ Error deleting user:', error);
    throw error;
  } finally {
    await sql.end();
  }
}

// Parse command line arguments
const args = process.argv.slice(2);

if (args.length === 0) {
  console.log(`
Usage:
  npm run delete-user -- <email>
  npm run delete-user -- --email <email>
  npm run delete-user -- --id <user-id>

Examples:
  npm run delete-user -- user@example.com
  npm run delete-user -- --email user@example.com
  npm run delete-user -- --id usr_abc123

Environment:
  DEV_MODE=true   Use .env.local (default)
  DEV_MODE=false  Use .env.production
`);
  process.exit(1);
}

let identifier: string;
let isEmail = true;

if (args[0] === '--email') {
  identifier = args[1];
  isEmail = true;
} else if (args[0] === '--id') {
  identifier = args[1];
  isEmail = false;
} else {
  // Assume it's an email
  identifier = args[0];
  isEmail = true;
}

if (!identifier) {
  console.error('❌ No email or user ID provided');
  process.exit(1);
}

// Run the deletion
deleteUser(identifier, isEmail);
