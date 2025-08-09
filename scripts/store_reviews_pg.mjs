// scripts/store_reviews_pg.mjs
import fs from 'fs';
import path from 'path';
import gplay from 'google-play-scraper';
import pkg from 'pg';
const { Client } = pkg;

// --- Edit the user field if different ---
const client = new Client({
  user: "d2c-rahiman.s",
  host: "localhost",
  database: "samsung_feedback",
  password: "",
  port: 5432
});

function fmtTS(d) {
  const y = d.getUTCFullYear();
  const mm = String(d.getUTCMonth() + 1).padStart(2, '0');
  const dd = String(d.getUTCDate()).padStart(2, '0');
  const hh = String(d.getUTCHours()).padStart(2, '0');
  const min = String(d.getUTCMinutes()).padStart(2, '0');
  const ss = String(d.getUTCSeconds()).padStart(2, '0');
  return `${y}${mm}${dd}${hh}${min}${ss}`;
}

async function createTables() {
  await client.query(`
    CREATE TABLE IF NOT EXISTS user_reviews (
      id TEXT PRIMARY KEY,
      data JSONB,
      created_date TIMESTAMP,
      modified_date TIMESTAMP,
      source TEXT
    );
  `);

  await client.query(`
    CREATE TABLE IF NOT EXISTS bad_reviews (
      id TEXT PRIMARY KEY,
      data JSONB,
      created_date TIMESTAMP,
      modified_date TIMESTAMP,
      source TEXT
    );
  `);
}

async function upsertReview(table, review, source) {
  const now = new Date();
  await client.query(
    `
    INSERT INTO ${table} (id, data, created_date, modified_date, source)
    VALUES ($1, $2, $3, $4, $5)
    ON CONFLICT (id) DO UPDATE
    SET data = EXCLUDED.data,
        modified_date = EXCLUDED.modified_date,
        source = EXCLUDED.source
  `,
    [review.id, review, now, now, source]
  );
}

async function fetchAndStore() {
  await client.connect();
  await createTables();

  console.log("Fetching Play Store reviews...");
  const results = await gplay.reviews({
    appId: 'com.samsung.ecomm.global.in',
    sort: gplay.sort.NEWEST,
    num: 1000,
    throttle: 10
  });

  const reviews = results.data || [];
  console.log(`Fetched ${reviews.length} reviews`);

  // Filter bad reviews (score <= 3)
  const badReviews = reviews.filter(r => {
    try { return r.score !== undefined && Number(r.score) <= 3; }
    catch { return false; }
  });

  // --- Step 1: Save bad reviews JSON to disk with timestamped filename ---
  const ts = fmtTS(new Date());
  const outDir = path.resolve('./exports');
  if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });
  const outPath = path.join(outDir, `bad_Review_${ts}.json`);
  fs.writeFileSync(outPath, JSON.stringify(badReviews, null, 2), 'utf-8');
  console.log(`Saved ${badReviews.length} bad reviews to ${outPath}`);

  // --- Step 2: Upsert all reviews into DB, and bad ones also into bad_reviews ---
  let inserted = 0;
  let badInserted = 0;
  for (const r of reviews) {
    try {
      await upsertReview('user_reviews', r, 'google.playstore');
      inserted++;
      if (r.score !== undefined && Number(r.score) <= 3) {
        await upsertReview('bad_reviews', r, 'google.playstore');
        badInserted++;
      }
    } catch (err) {
      console.error(`Failed upsert for ${r.id}: ${err.message}`);
    }
  }

  console.log(`Stored/updated ${inserted} reviews in user_reviews`);
  console.log(`Stored/updated ${badInserted} bad reviews in bad_reviews`);

  await client.end();
}

(async () => {
  try {
    await fetchAndStore();
  } catch (err) {
    console.error("Error:", err);
    process.exit(1);
  }
})();
