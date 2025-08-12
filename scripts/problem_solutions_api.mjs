// // scripts/problem_solutions_api.mjs
// import express from "express";
// import cors from "cors";
// import pkg from "pg";
// import dotenv from "dotenv";

// dotenv.config();
// const { Pool } = pkg;

// const app = express();
// app.use(cors());
// app.use(express.json());

// // DB pool - reads creds from env with sensible defaults
// const pool = new Pool({
//   user: process.env.PGUSER || "d2c-rahiman.s",
//   host: process.env.PGHOST || "localhost",
//   database: process.env.PGDATABASE || "samsung_feedback",
//   password: process.env.PGPASSWORD || "",
//   port: Number(process.env.PGPORT || 5432),
//   max: 10,
//   idleTimeoutMillis: 30000,
// });

// // Simple health-check route
// app.get("/health", async (req, res) => {
//   try {
//     const { rows } = await pool.query("SELECT 1 as ok");
//     res.json({ ok: true });
//   } catch (err) {
//     console.error("DB health check failed:", err);
//     res.status(500).json({ ok: false, error: err.message });
//   }
// });

// /*
//  GET /api/problem_solutions
//  Returns all rows (with optional filters and pagination).
//  Query params:
//   - category (string)
//   - module (string)
//   - limit (int) default 100
//   - offset (int) default 0
//   - from_date, to_date (YYYY-MM-DD or ISO format) to filter created_date
// */
// app.get("/api/problem_solutions", async (req, res) => {
//   try {
//     const { category, module, limit = 100, offset = 0, from_date, to_date } = req.query;

//     let where = [];
//     let params = [];
//     let idx = 1;

//     if (category) {
//       where.push(`category ILIKE $${idx++}`);
//       params.push(category);
//     }
//     if (module) {
//       where.push(`module ILIKE $${idx++}`);
//       params.push(module);
//     }
//     if (from_date) {
//       where.push(`created_date >= $${idx++}`);
//       params.push(from_date);
//     }
//     if (to_date) {
//       where.push(`created_date <= $${idx++}`);
//       params.push(to_date);
//     }

//     const whereClause = where.length ? "WHERE " + where.join(" AND ") : "";

//     const sql = `
//       SELECT id, cluster_id, problem_statement, solutions, category, module, issue,
//              impact_score, solvability_score, occurrence, source, created_date, modified_date
//       FROM problem_solutions
//       ${whereClause}
//       ORDER BY created_date DESC
//       LIMIT $${idx++} OFFSET $${idx++}
//     `;
//     params.push(Number(limit));
//     params.push(Number(offset));

//     const { rows } = await pool.query(sql, params);

//     // rows will contain solutions as parsed JS objects (pg parses JSONB)
//     res.json(rows);
//   } catch (err) {
//     console.error("Error querying problem_solutions:", err);
//     res.status(500).json({ error: err.message });
//   }
// });

// // optional: fetch single record by id
// app.get("/api/problem_solutions/:id", async (req, res) => {
//   try {
//     const { id } = req.params;
//     const { rows } = await pool.query(
//       `SELECT * FROM problem_solutions WHERE id = $1 LIMIT 1`, [id]
//     );
//     if (!rows.length) return res.status(404).json({ error: "not found" });
//     return res.json(rows[0]);
//   } catch (err) {
//     console.error(err);
//     res.status(500).json({ error: err.message });
//   }
// });

// const PORT = process.env.SOL_API_PORT || 3002;
// app.listen(PORT, () => {
//   console.log(`problem_solutions API listening at http://localhost:${PORT}`);
// });


// New code to handle both post and get request..


// scripts/problem_solutions_api.mjs
import express from "express";
import cors from "cors";
import pkg from "pg";
import dotenv from "dotenv";

dotenv.config();
const { Pool } = pkg;

const app = express();
app.use(cors());
app.use(express.json());

const pool = new Pool({
  user: process.env.PGUSER || "d2c-rahiman.s",
  host: process.env.PGHOST || "localhost",
  database: process.env.PGDATABASE || "samsung_feedback",
  password: process.env.PGPASSWORD || "",
  port: Number(process.env.PGPORT || 5432),
  max: 10,
  idleTimeoutMillis: 30000,
});

function isYYYYMMDDHHMMSS(s) {
  return typeof s === "string" && /^\d{14}$/.test(s);
}

function buildFiltersFromParams({ issue_type, module, from_date, to_date }) {
  const where = [];
  const params = [];
  let idx = 1;

  if (issue_type) {
    where.push(`LOWER(category) = LOWER($${idx++})`);
    params.push(issue_type);
  }
  if (module) {
    where.push(`LOWER(module) = LOWER($${idx++})`);
    params.push(module);
  }
  if (from_date) {
    if (isYYYYMMDDHHMMSS(from_date)) {
      where.push(`created_date >= to_timestamp($${idx++}, 'YYYYMMDDHH24MISS')`);
      params.push(from_date);
    } else {
      // expects ISO or DB-parseable date string
      where.push(`created_date >= $${idx++}`);
      params.push(from_date);
    }
  }
  if (to_date) {
    if (isYYYYMMDDHHMMSS(to_date)) {
      where.push(`created_date <= to_timestamp($${idx++}, 'YYYYMMDDHH24MISS')`);
      params.push(to_date);
    } else {
      where.push(`created_date <= $${idx++}`);
      params.push(to_date);
    }

  }

  return { where, params, nextIndex: idx };
}

// health check
app.get("/health", async (req, res) => {
  try {
    await pool.query("SELECT 1");
    res.json({ ok: true });
  } catch (err) {
    console.error("DB health check failed:", err);
    res.status(500).json({ ok: false, error: err.message });
  }
});

/*
  GET /api/problem_solutions
  Query params: category, module, from_date, to_date, limit, offset
  from_date / to_date can be YYYYMMDDHHMMSS OR ISO-format strings.
*/
app.get("/api/problem_solutions", async (req, res) => {
  try {
    const { category, module, from_date, to_date } = req.query;
    const limit = Number(req.query.limit || 100);
    const offset = Number(req.query.offset || 0);

    const filters = buildFiltersFromParams({
      issue_type: category,
      module,
      from_date,
      to_date,
    });

    const whereClause = filters.where.length ? "WHERE " + filters.where.join(" AND ") : "";

    // add limit/offset placeholders
    const sql = `
      SELECT id, cluster_id, problem_statement, solutions, category, module, issue,
             impact_score, solvability_score, occurrence, source, created_date, modified_date
      FROM problem_solutions
      ${whereClause}
      ORDER BY created_date DESC
      LIMIT $${filters.nextIndex} OFFSET $${filters.nextIndex + 1}
    `;
    const params = [...filters.params, limit, offset];

    console.log("SQL:", sql);
    console.log("PARAMS:", params);

    const { rows } = await pool.query(sql, params);
    res.json(rows);
  } catch (err) {
    console.error("Error querying GET /api/problem_solutions:", err);
    res.status(500).json({ error: err.message });
  }
});

/*
  POST /api/problem_solutions
  Body JSON:
    {
      "issue_type": "platform",
      "from_date": "20250101000000",
      "to_date": "20250811000000",
      "module": "Delivery",           // optional
      "limit": 100, "offset": 0       // optional
    }
  Date strings can be 14-digit YYYYMMDDHHMMSS or ISO timestamps.
*/
app.post("/api/problem_solutions", async (req, res) => {
  try {
    const { issue_type, module, from_date, to_date } = req.body;
    const limit = Number(req.body.limit || 100);
    const offset = Number(req.body.offset || 0);

    if (!issue_type) {
      return res.status(400).json({ error: "issue_type required in request body" });
    }

    const filters = buildFiltersFromParams({
      issue_type,
      module,
      from_date,
      to_date,
    });

    const whereClause = filters.where.length ? "WHERE " + filters.where.join(" AND ") : "";

    const sql = `
      SELECT id, cluster_id, problem_statement, solutions, category, module, issue,
             impact_score, solvability_score, occurrence, source, created_date, modified_date
      FROM problem_solutions
      ${whereClause}
      ORDER BY created_date DESC
      LIMIT $${filters.nextIndex} OFFSET $${filters.nextIndex + 1}
    `;
    const params = [...filters.params, limit, offset];

    console.log("POST SQL:", sql);
    console.log("POST PARAMS:", params);

    const { rows } = await pool.query(sql, params);
    res.json(rows);
  } catch (err) {
    console.error("Error querying POST /api/problem_solutions:", err);
    res.status(500).json({ error: err.message });
  }
});

// fetch single record
app.get("/api/problem_solutions/:id", async (req, res) => {
  try {
    const { id } = req.params;
    const { rows } = await pool.query(`SELECT * FROM problem_solutions WHERE id = $1 LIMIT 1`, [id]);
    if (!rows.length) return res.status(404).json({ error: "not found" });
    res.json(rows[0]);
  } catch (err) {
    console.error("Error GET by id:", err);
    res.status(500).json({ error: err.message });
  }
});

const PORT = process.env.SOL_API_PORT || 3002;
app.listen(PORT, () => {
  console.log(`problem_solutions API listening at http://localhost:${PORT}`);
});
