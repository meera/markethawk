import { drizzle } from 'drizzle-orm/postgres-js';
import postgres from 'postgres';
import * as schema from './schema';

// Database connection
const connectionString = process.env.DATABASE_URL!;

if (!connectionString) {
  throw new Error('DATABASE_URL environment variable is not set');
}

// Create postgres client
export const client = postgres(connectionString);

// Create drizzle instance with schema
export const db = drizzle(client, { schema });

// Helper function to close connection (for scripts)
export async function closeDb() {
  await client.end();
}
