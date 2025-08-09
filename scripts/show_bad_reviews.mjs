import sqlite3 from "sqlite3";
import { open } from "sqlite";

async function initDB() {
  return open({
    filename: './data/reviews.db',
    driver: sqlite3.Database
  });
}

async function showBadReviews(limit = 10, keyword = null, dateFrom = null) {
  const db = await initDB();

  let query = `
    SELECT id, data, created_date, modified_date
    FROM bad_reviews
    WHERE 1=1
  `;
  const params = [];

  if (keyword) {
    query += ` AND LOWER(data) LIKE ?`;
    params.push(`%${keyword.toLowerCase()}%`);
  }

  if (dateFrom) {
    query += ` AND date(created_date) >= date(?)`;
    params.push(dateFrom);
  }

  query += ` ORDER BY created_date DESC LIMIT ?`;
  params.push(limit);

  const rows = await db.all(query, params);

  console.log(`\n=== Showing ${rows.length} Bad Reviews${keyword ? ` matching "${keyword}"` : ""}${dateFrom ? ` since ${dateFrom}` : ""} ===`);
  for (const row of rows) {
    let review;
    try {
      review = JSON.parse(row.data);
    } catch {
      review = {};
    }
    console.log(`
ID: ${row.id}
User: ${review.userName || "N/A"}
Score: ${review.score || "N/A"}
Date: ${review.date || "N/A"}
Text: ${review.text || ""}
Created: ${row.created_date}
Modified: ${row.modified_date}
--------------------------------`);
  }

  await db.close();
}

(async () => {
  const limit = process.argv[2] ? parseInt(process.argv[2], 10) : 10;
  const keyword = process.argv[3] && process.argv[3] !== "null" ? process.argv[3] : null;
  const dateFrom = process.argv[4] && process.argv[4] !== "null" ? process.argv[4] : null;

  await showBadReviews(limit, keyword, dateFrom);
})();
