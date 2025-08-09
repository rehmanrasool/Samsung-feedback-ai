import gplay from "google-play-scraper";
import sqlite3 from "sqlite3";
import { open } from "sqlite";

// Open or create DB
async function initDB() {
  return open({
    filename: './data/reviews.db',
    driver: sqlite3.Database
  });
}

// Create tables if not exists
async function createTables(db) {
  await db.exec(`
    CREATE TABLE IF NOT EXISTS user_reviews (
      id TEXT PRIMARY KEY,
      data TEXT,
      created_date TEXT,
      modified_date TEXT
    )
  `);

  await db.exec(`
    CREATE TABLE IF NOT EXISTS bad_reviews (
      id TEXT PRIMARY KEY,
      data TEXT,
      created_date TEXT,
      modified_date TEXT
    )
  `);
}

// Insert or update a record in given table
async function upsertReview(db, table, review) {
  const now = new Date().toISOString();
  const jsonData = JSON.stringify(review);

  await db.run(
    `INSERT INTO ${table} (id, data, created_date, modified_date)
     VALUES (?, ?, ?, ?)
     ON CONFLICT(id) DO UPDATE SET
       data = excluded.data,
       modified_date = excluded.modified_date`,
    [review.id, jsonData, now, now]
  );
}

async function fetchAndStore() {
  const db = await initDB();
  await createTables(db);

  console.log("Fetching Play Store reviews...");
  const results = await gplay.reviews({
    appId: 'com.samsung.ecomm.global.in',
    sort: gplay.sort.NEWEST,
    num: 1000,
    throttle: 10
  });

  const reviews = results.data;
  console.log(`Fetched ${reviews.length} reviews`);

  let badCount = 0;

  for (const r of reviews) {
    await upsertReview(db, "user_reviews", r);

    // Check for bad review
    if (r.score !== undefined && r.score <= 3) {
      await upsertReview(db, "bad_reviews", r);
      badCount++;
    }
  }

  console.log(`Stored ${reviews.length} total reviews`);
  console.log(`Stored ${badCount} bad reviews`);

  await db.close();
}

(async () => {
  await fetchAndStore();
})();
