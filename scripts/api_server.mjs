// scripts/api_server.mjs
import express from 'express';
import pkg from 'pg';
const { Pool } = pkg;

const pool = new Pool({
  user: "d2c-rahiman.s",
  host: "localhost",
  database: "samsung_feedback",
  password: "",
  port: 5432
});

const app = express();
app.use(express.json());

// Accept many possible key names from client
function getField(body, ...names) {
  for (const n of names) if (body[n] !== undefined) return body[n];
  return undefined;
}

// Parse YYYYMMDDHHMMSS -> ISO string (UTC)
function parseYYYYMMDDHHMMSS(s) {
  if (!s) return null;
  const digits = String(s).replace(/\D/g, '');
  if (digits.length === 14) {
    const y = digits.slice(0,4), mo = digits.slice(4,6), d = digits.slice(6,8);
    const hh = digits.slice(8,10), mm = digits.slice(10,12), ss = digits.slice(12,14);
    return `${y}-${mo}-${d}T${hh}:${mm}:${ss}Z`;
  }
  // fallback try native parse
  const dt = new Date(s);
  if (!isNaN(dt)) return dt.toISOString();
  return null;
}

app.post('/reviews', async (req, res) => {
  try {
    const body = req.body || {};
    const source = getField(body, 'source', 'Source');
    const isBad = getField(body, 'is_bad_review', 'isBad', 'is_bad', 'isBadReview') === true;
    const rawFrom = getField(body, 'from_date', 'From date', 'fromDate', 'from');
    const rawTo = getField(body, 'to_date', 'to date', 'toDate', 'to');

    const fromISO = parseYYYYMMDDHHMMSS(rawFrom) || '1970-01-01T00:00:00Z';
    const toISO = parseYYYYMMDDHHMMSS(rawTo) || new Date().toISOString();

    // choose table safely
    const table = isBad ? 'bad_reviews' : 'user_reviews';

    // Build dynamic where clause and params
    const where = [];
    const params = [];

    if (source) {
      params.push(source);
      where.push(`source = $${params.length}`);
    }

    // Compare using JSON field (data->>'date') cast to timestamptz
    params.push(fromISO);
    where.push(`(data->>'date')::timestamptz >= $${params.length}::timestamptz`);
    params.push(toISO);
    where.push(`(data->>'date')::timestamptz <= $${params.length}::timestamptz`);

    const query = `
      SELECT (data->>'text') AS text,
             (data->>'score')::int AS score,
             (data->>'date') AS date
      FROM ${table}
      WHERE ${where.join(' AND ')}
      ORDER BY (data->>'date')::timestamptz DESC
      LIMIT 1000
    `;

    const { rows } = await pool.query(query, params);
    // rows already contain text, score, date
    res.json(rows);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: err.message });
  }
});

const PORT = 4000;
app.listen(PORT, () => {
  console.log(`API server listening at http://localhost:${PORT}`);
});
