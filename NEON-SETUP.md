# Neon Database Setup for Production

## 1. Create Neon Project

**URL:** https://console.neon.tech

1. Sign up/login with GitHub
2. Create new project:
   - Name: `markethawk-production`
   - Region: `US East (Ohio)` or closest to users
   - Postgres: 16

3. Copy connection string from dashboard

## 2. Configure Environment Variables

### Development (Local)

File: `web/.env`
```bash
DATABASE_URL="postgresql://postgres:postgres@192.168.86.250:54322/postgres"
```

### Production (Vercel/Deployment)

Add to Vercel environment variables:
```bash
DATABASE_URL="postgresql://[user]:[password]@[neon-host]/[database]?sslmode=require"
```

**Important:** The Neon connection string includes `?sslmode=require` - keep this!

## 3. Import Data to Neon

### Option A: From Local Machine

```bash
# Set Neon connection string temporarily
export DATABASE_URL="postgresql://[user]:[password]@[neon-host]/[database]?sslmode=require"

# Import data
cd ~/markethawk
source .venv/bin/activate
python lens/scripts/import_nasdaq_screener.py --csv-file data/nasdaq_screener.csv
```

### Option B: From Production Server

```bash
# 1. Upload CSV to server
scp data/nasdaq_screener.csv user@server:/var/markethawk/data/

# 2. SSH to server
ssh user@server

# 3. Set environment variable
export DATABASE_URL="postgresql://[user]:[password]@[neon-host]/[database]?sslmode=require"

# 4. Run import
cd /var/markethawk
python lens/scripts/import_nasdaq_screener.py
```

## 4. Verify Import

```bash
# Connect with psql
psql "postgresql://[user]:[password]@[neon-host]/[database]?sslmode=require"

# Check data
SELECT COUNT(*) FROM markethawkeye.companies;
SELECT * FROM markethawkeye.companies LIMIT 5;
```

## 5. Neon Connection Pooling (Recommended)

Neon provides **connection pooling** for better performance with serverless:

**Pooled Connection String:**
```
postgresql://[user]:[password]@[neon-host]/[database]?sslmode=require&pgbouncer=true
```

Add `&pgbouncer=true` to enable connection pooling.

## 6. Production Deployment (Vercel)

### Set Environment Variables in Vercel

1. Go to: https://vercel.com/[your-team]/markethawk/settings/environment-variables

2. Add:
   - `DATABASE_URL` = `postgresql://[user]:[password]@[neon-host]/[database]?sslmode=require&pgbouncer=true`
   - `NEXT_PUBLIC_BASE_URL` = `https://markethawkeye.com`

3. Redeploy:
   ```bash
   git push  # Automatic deployment
   ```

## Neon Features

### Branching (Optional)
Create database branches for staging:
```bash
# In Neon console, create a branch called "staging"
# Get staging connection string
# Use for preview deployments
```

### Autoscaling
- Neon automatically scales compute up/down
- Free tier: 0.5 GB storage, 0.25 vCPU
- Paid: Auto-scales from 0.25 to 8 vCPUs

### Backups
- Neon automatically backs up your data
- Point-in-time recovery available
- 7-day retention on free tier

## Cost Optimization

**Free Tier Limits:**
- 0.5 GB storage
- 100 hours compute/month (3 GB-hours)
- 1 project, 10 branches

**For Production:**
- Pro plan: $19/month
- Unlimited compute hours
- 10 GB storage included
- Auto-scaling

## Troubleshooting

### psql Connection Timeout (SOLVED)

**Problem:** psql hangs when connecting to Neon

**Solution:** Explicitly specify port 5432 in connection string

```bash
# ❌ Without port (may try wrong port)
psql "postgresql://user:pass@host/db?sslmode=require"

# ✅ With port 5432 (works)
psql "postgresql://user:pass@host:5432/db?sslmode=require"
```

**Why:** Some networks block non-standard PostgreSQL ports. Always use `:5432` for psql commands.

### CSV Import with COPY

If importing directly with psql `\COPY`:

```bash
# 1. Clean CSV first (remove $ and % symbols)
python3 << 'EOF'
import csv
from pathlib import Path

input_file = Path('data/nasdaq_screener.csv')
output_file = Path('data/nasdaq_screener_cleaned.csv')

with input_file.open('r') as f_in:
    reader = csv.DictReader(f_in)
    with output_file.open('w', newline='') as f_out:
        writer = csv.DictWriter(f_out, fieldnames=reader.fieldnames)
        writer.writeheader()
        for row in reader:
            cleaned = {k: v.replace('$','').replace('%','') for k, v in row.items()}
            writer.writerow(cleaned)
EOF

# 2. Import cleaned CSV
psql "postgresql://user:pass@host:5432/db?sslmode=require" \
  -c "\COPY markethawkeye.companies (symbol, name, last_sale, net_change, pct_change, market_cap, country, ipo_year, volume, sector, industry) FROM 'data/nasdaq_screener_cleaned.csv' DELIMITER ',' CSV HEADER"
```

### Connection Timeout
```bash
# Add connection timeout
DATABASE_URL="postgresql://[user]:[password]@[neon-host]:5432/[database]?sslmode=require&connect_timeout=10"
```

### SSL Certificate Issues
```bash
# Neon requires SSL
# Make sure sslmode=require is in connection string
```

### Too Many Connections
```bash
# Use connection pooling
DATABASE_URL="postgresql://[user]:[password]@[neon-host]:5432/[database]?sslmode=require&pgbouncer=true"
```

## Schema Migration (If Needed)

If schema doesn't exist in Neon, the import script will create it automatically.

The script creates:
- Schema: `markethawkeye`
- Table: `markethawkeye.companies`
- Indexes on: symbol, name, sector, industry, market_cap

## Monitoring

**Neon Console:** https://console.neon.tech/app/projects/[project-id]

Monitor:
- Query performance
- Storage usage
- Compute usage
- Active connections

## Security Best Practices

1. **Never commit credentials to git**
   - Keep `.env` in `.gitignore`
   - Use environment variables

2. **Use connection pooling** for serverless (Vercel)
   - Add `&pgbouncer=true` to connection string

3. **Rotate credentials** periodically
   - Reset password in Neon console
   - Update environment variables

4. **Use separate databases** for dev/staging/prod
   - Development: Local PostgreSQL
   - Staging: Neon branch
   - Production: Neon main branch

## Quick Reference

**Local Dev:**
```bash
DATABASE_URL="postgresql://postgres:postgres@192.168.86.250:54322/postgres"
```

**Neon Production:**
```bash
DATABASE_URL="postgresql://[user]:[password]@[neon-host]/[database]?sslmode=require&pgbouncer=true"
```

**Import Command:**
```bash
python lens/scripts/import_nasdaq_screener.py
```

**Verify:**
```sql
SELECT COUNT(*) FROM markethawkeye.companies;  -- Should be ~7,600
```
