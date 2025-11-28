#!/usr/bin/env node

/**
 * Upload rendered video to Cloudflare R2
 *
 * Usage:
 *   node scripts/upload-to-r2.js --ticker=AAPL --quarter=Q4 --year=2024
 *
 * This will:
 * 1. Create R2 directory structure: markethawk/AAPL/videos/
 * 2. Upload: studio/out/AAPL-Q4-2024.mp4 → markethawk/AAPL/videos/2024-Q4-full.mp4
 * 3. Verify upload
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Parse command line arguments
const args = process.argv.slice(2).reduce((acc, arg) => {
  const [key, value] = arg.replace('--', '').split('=');
  acc[key] = value;
  return acc;
}, {});

const { ticker, quarter, year } = args;

if (!ticker || !quarter || !year) {
  console.error('❌ Missing required arguments');
  console.log('Usage: node scripts/upload-to-r2.js --ticker=AAPL --quarter=Q4 --year=2024');
  process.exit(1);
}

const BUCKET = 'markethawkeye';
const REMOTE = 'r2-public'; // Use existing r2-public remote from CLAUDE.md

// File paths
const localFile = path.join(__dirname, '..', 'studio', 'out', `${ticker}-${quarter}-${year}.mp4`);
const r2Path = `${ticker}/videos/${year}-${quarter}-full.mp4`;

console.log('📤 Uploading to R2...\n');
console.log(`Local file: ${localFile}`);
console.log(`R2 path: ${REMOTE}:${BUCKET}/${r2Path}\n`);

// Check if local file exists
if (!fs.existsSync(localFile)) {
  console.error(`❌ File not found: ${localFile}`);
  console.log('\nMake sure you\'ve rendered the video first:');
  console.log(`  cd studio && npm run render -- --props='@./data/${ticker}-${quarter}-${year}.json'`);
  process.exit(1);
}

try {
  // Create R2 directory structure
  console.log('1️⃣ Creating R2 directory structure...');
  execSync(`rclone mkdir ${REMOTE}:${BUCKET}/${ticker}`, { stdio: 'inherit' });
  execSync(`rclone mkdir ${REMOTE}:${BUCKET}/${ticker}/videos`, { stdio: 'inherit' });
  console.log('✅ Directories created\n');

  // Upload video
  console.log('2️⃣ Uploading video...');
  execSync(`rclone copy "${localFile}" ${REMOTE}:${BUCKET}/${ticker}/videos/ -P`, { stdio: 'inherit' });
  console.log('✅ Upload complete\n');

  // Verify upload
  console.log('3️⃣ Verifying upload...');
  const result = execSync(`rclone ls ${REMOTE}:${BUCKET}/${ticker}/videos/`).toString();
  console.log(result);

  if (result.includes(`${year}-${quarter}-full.mp4`)) {
    console.log('✅ Upload verified successfully!\n');
    console.log(`🔗 R2 URL: https://pub-xxx.r2.dev/${ticker}/videos/${year}-${quarter}-full.mp4`);
    console.log('\n📝 Next steps:');
    console.log('1. Upload video to YouTube');
    console.log('2. Update database with YouTube ID and R2 URL');
    console.log('3. Test video page on website');
  } else {
    console.error('❌ Upload verification failed');
    process.exit(1);
  }
} catch (error) {
  console.error('❌ Upload failed:', error.message);
  process.exit(1);
}
