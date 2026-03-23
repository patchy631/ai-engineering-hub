const db = require("./db");
const { v4: uuidv4 } = require("uuid");

const VALID_STATUSES = ["todo", "in_progress", "review", "done"];
const VALID_PRIORITIES = ["p0", "p1", "p2", "p3"];

const Task = {
  create({ title, description, status = "todo", priority = "p2", assigneeId, createdBy, dueDate }) {
    const id = uuidv4();

    const stmt = db.prepare(`
      INSERT INTO tasks (id, title, description, status, priority, assignee_id, created_by, due_date)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    `);
    stmt.run(id, title, description || null, status, priority, assigneeId || null, createdBy, dueDate || null);

    return Task.findById(id);
  },

  findById(id) {
    const stmt = db.prepare(`
      SELECT t.*, u.name as assignee_name
      FROM tasks t
      LEFT JOIN users u ON t.assignee_id = u.id
      WHERE t.id = ?
    `);
    return stmt.get(id);
  },

  findAll({ status, assigneeId, createdBy } = {}) {
    let query = `
      SELECT t.*, u.name as assignee_name
      FROM tasks t
      LEFT JOIN users u ON t.assignee_id = u.id
      WHERE 1=1
    `;
    const params = [];

    if (status) {
      query += " AND t.status = ?";
      params.push(status);
    }
    if (assigneeId) {
      query += " AND t.assignee_id = ?";
      params.push(assigneeId);
    }
    if (createdBy) {
      query += " AND t.created_by = ?";
      params.push(createdBy);
    }

    query += " ORDER BY t.created_at DESC";

    const stmt = db.prepare(query);
    return stmt.all(...params);
  },

  update(id, fields) {
    const allowed = ["title", "description", "status", "priority", "assignee_id", "due_date"];
    const updates = [];
    const values = [];

    for (const [key, value] of Object.entries(fields)) {
      if (allowed.includes(key)) {
        if (key === "status" && !VALID_STATUSES.includes(value)) {
          throw new Error(`Invalid status: ${value}. Must be one of: ${VALID_STATUSES.join(", ")}`);
        }
        if (key === "priority" && !VALID_PRIORITIES.includes(value)) {
          throw new Error(`Invalid priority: ${value}. Must be one of: ${VALID_PRIORITIES.join(", ")}`);
        }
        updates.push(`${key} = ?`);
        values.push(value);
      }
    }

    if (updates.length === 0) return Task.findById(id);

    updates.push("updated_at = datetime('now')");
    values.push(id);

    const stmt = db.prepare(`UPDATE tasks SET ${updates.join(", ")} WHERE id = ?`);
    stmt.run(...values);

    return Task.findById(id);
  },

  delete(id) {
    const stmt = db.prepare("DELETE FROM tasks WHERE id = ?");
    return stmt.run(id);
  },

  countByUser(userId) {
    const stmt = db.prepare(`
      SELECT
        COUNT(*) as total,
        SUM(CASE WHEN status = 'done' THEN 1 ELSE 0 END) as completed,
        SUM(CASE WHEN status != 'done' THEN 1 ELSE 0 END) as active
      FROM tasks
      WHERE assignee_id = ? OR created_by = ?
    `);
    return stmt.get(userId, userId);
  },
};

module.exports = Task;
