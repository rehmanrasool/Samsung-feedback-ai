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

// PostgreSQL connection
const pool = new Pool({
  user: process.env.PGUSER || "d2c-rahiman.s",
  host: process.env.PGHOST || "localhost",
  database: process.env.PGDATABASE || "samsung_feedback",
  password: process.env.PGPASSWORD || "",
  port: Number(process.env.PGPORT || 5432),
});

// Health check
app.get("/health", async (req, res) => {
  try {
    await pool.query("SELECT 1");
    res.json({ status: "ok" });
  } catch (err) {
    res.status(500).json({ status: "error", error: err.message });
  }
});

/**
 * POST /api/problem_solutions
 * Filters: category, from_date, to_date
 */
app.post("/api/problem_solutions", async (req, res) => {
  try {
    const { category, from_date, to_date } = req.body;

    if (!category || !from_date || !to_date) {
      return res.status(400).json({ error: "category, from_date, and to_date are required" });
    }

    const sql = `
      SELECT 
        problem_statement,
        solutions,
        category,
        module,
        impact_score,
        solvability_score,
        issue,
        occurrence,
        source,
        created_date,
        modified_date
      FROM problem_solutions
      WHERE category ILIKE $1
        AND created_date >= $2
        AND created_date <= $3
      ORDER BY created_date DESC
    `;

    const { rows } = await pool.query(sql, [category, from_date, to_date]);

    res.json(rows);
  } catch (err) {
    console.error("Error fetching problem_solutions:", err);
    res.status(500).json({ error: err.message });
  }
});

// Start API
const PORT = process.env.SOL_API_PORT || 3003;
app.listen(PORT, () => {
  console.log(`problem_solutions API running on http://localhost:${PORT}`);
});
