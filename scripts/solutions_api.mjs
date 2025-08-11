// scripts/solutions_api.mjs
import express from "express";
import bodyParser from "body-parser";
import pkg from "pg";

const { Pool } = pkg;

// DB connection
const pool = new Pool({
  user: "d2c-rahiman.s", // change if needed
  host: "localhost",
  database: "samsung_feedback",
  port: 5432,
});

const app = express();
app.use(bodyParser.json());

// API: Get problem statement + recommendations
app.post("/api/solutions", async (req, res) => {
  try {
    const { issue_type, from_date, to_date } = req.body;

    if (!issue_type || !from_date || !to_date) {
      return res.status(400).json({
        error: "Missing required fields: issue_type, from_date, to_date",
      });
    }

    // Convert from YYYYMMDDHHMMSS to ISO
    const fromISO = `${from_date.slice(0,4)}-${from_date.slice(4,6)}-${from_date.slice(6,8)}T${from_date.slice(8,10)}:${from_date.slice(10,12)}:${from_date.slice(12,14)}Z`;
    const toISO = `${to_date.slice(0,4)}-${to_date.slice(4,6)}-${to_date.slice(6,8)}T${to_date.slice(8,10)}:${to_date.slice(10,12)}:${to_date.slice(12,14)}Z`;

    // Query DB for matching reviews
    const result = await pool.query(
      `SELECT id, data->>'text' AS text, created_date
       FROM classified_reviews
       WHERE category = $1
       AND created_date BETWEEN $2 AND $3`,
      [issue_type, fromISO, toISO]
    );

    const occurrence = result.rows.length;

    // ====== Stubbed values for now ======
    const problemStatement =
      "Checkout process on the Samsung app is slow and fails during payment for many users.";
    const recommendedSolutions = [
      "Optimize payment gateway API integration for faster response times.",
      "Implement retry mechanism for failed transactions.",
      "Add better error messaging for payment failures to guide users."
    ];
    const solvabilityScore = 4; // 1-5 scale
    const impactScore = 4; // 1-5 scale

    res.json({
      problem_statement: problemStatement,
      recommended_solutions: recommendedSolutions,
      solvability_score: solvabilityScore,
      impact_score: impactScore,
      occurrence: occurrence
    });

  } catch (err) {
    console.error("Error in /api/solutions:", err);
    res.status(500).json({ error: "Internal server error" });
  }
});

// Start server
app.listen(3001, () => {
  console.log("Solutions API running on http://localhost:3001");
});
