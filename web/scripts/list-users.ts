#!/usr/bin/env tsx
import { drizzle } from 'drizzle-orm/postgres-js';
import postgres from 'postgres';
import { user } from '../lib/db/auth-schema';
import dotenv from 'dotenv';
import { resolve } from 'path';

const isDev = process.env.DEV_MODE !== 'false';
const envFile = isDev ? '.env.local' : '.env.production';
const envPath = resolve(process.cwd(), envFile);

dotenv.config({ path: envPath });

const sql = postgres(process.env.DATABASE_URL!);
const db = drizzle(sql, {});

async function listUsers() {
  const users = await db.select({
    id: user.id,
    email: user.email,
    name: user.name,
    createdAt: user.createdAt
  }).from(user);

  console.log(`\nUsers in ${envFile}:\n`);
  if (users.length === 0) {
    console.log('  No users found');
  } else {
    users.forEach(u => {
      console.log(`  - ${u.email}`);
      console.log(`    ID: ${u.id}`);
      console.log(`    Name: ${u.name || 'N/A'}`);
      console.log(`    Created: ${u.createdAt}`);
      console.log('');
    });
  }

  await sql.end();
}

listUsers();
