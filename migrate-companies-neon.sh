#!/bin/bash
#
# Migrate companies database to Neon production
#
# Usage:
#   bash migrate-companies-neon.sh
#
# This script:
# 1. Drops and recreates companies table in Neon
# 2. Imports data from companies_master.csv
#
# WARNING: This will delete all existing company data in Neon!

set -e

NEON_URL="postgresql://neondb_owner:npg_e1uBMOdh5QUy@ep-twilight-leaf-a4dgbd70-pooler.us-east-1.aws.neon.tech:5432/neondb?sslmode=require&channel_binding=require"

echo "🦅 MARKEY HAWKEYE - Migrate to Neon Production"
echo "=============================================="
echo ""
echo "⚠️  WARNING: This will DELETE and RECREATE the companies table!"
echo ""
read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ Aborted"
    exit 1
fi

echo ""
echo "🔌 Migrating to Neon..."
echo ""

# Run migration script with Neon URL
source .venv/bin/activate
DATABASE_URL="$NEON_URL" python lens/scripts/migrate_companies_db.py

echo ""
echo "✅ Migration complete!"
echo ""
echo "📊 Verify at: https://console.neon.tech"
