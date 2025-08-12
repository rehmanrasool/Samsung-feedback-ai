// problem_solution_api.mjs
import express from 'express';
import pkg from 'pg';
const { Pool } = pkg;

const pool = new Pool({
  user: 'postgres', // change if needed
  host: 'localhost',
  database: 'samsung_feedback', // match your DB name
  password: 'your_password',    // change if needed
  port: 5432,
});

const app = express();
app.use(express.json());

// POST API to fetch problem_solutions
app.post('/api/problem_solutions', async (req, res) => {
  try {
    const { issue_type, from_date, to_date } = req.body;

    if (!issue_type || !from_date || !to_date) {
      return res.status(400).json({ error: 'Missing required fields' });
    }

    const query = `
      SELECT *
      FROM problem_solutions
      WHERE LOWER(category) = LOWER($1)
        AND created_date >= to_timestamp($2, 'YYYYMMDDHH24MISS')
        AND created_date <= to_timestamp($3, 'YYYYMMDDHH24MISS')
    `;

    const { rows } = await pool.query(query, [issue_type, from_date, to_date]);

    if (rows.length === 0) {
      return res.json([]); // No matches found
    }

    res.json(rows);
  } catch (err) {
    console.error("Error querying POST /api/problem_solutions:", err);
    res.status(500).json({ error: err.stack, details: err });
  }

//console.error("Error querying POST /api/problem_solutions:", err);
//res.status(500).json({ error: err.stack, details: err });


});

// Start server
app.listen(3002, () => {
  console.log('Problem Solutions API running on port 3002');
});
