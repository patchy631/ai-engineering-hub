const db = require("./db");
const { v4: uuidv4 } = require("uuid");
const bcrypt = require("bcryptjs");

const User = {
  create({ email, name, password, role = "member" }) {
    const id = uuidv4();
    const passwordHash = bcrypt.hashSync(password, 10);

    const stmt = db.prepare(`
      INSERT INTO users (id, email, name, password_hash, role)
      VALUES (?, ?, ?, ?, ?)
    `);
    stmt.run(id, email, name, passwordHash, role);

    return User.findById(id);
  },

  findById(id) {
    const stmt = db.prepare("SELECT id, email, name, role, created_at, updated_at FROM users WHERE id = ?");
    return stmt.get(id);
  },

  findByEmail(email) {
    const stmt = db.prepare("SELECT * FROM users WHERE email = ?");
    return stmt.get(email);
  },

  findAll() {
    const stmt = db.prepare("SELECT id, email, name, role, created_at FROM users");
    return stmt.all();
  },

  update(id, fields) {
    const allowed = ["name", "email", "role"];
    const updates = [];
    const values = [];

    for (const [key, value] of Object.entries(fields)) {
      if (allowed.includes(key)) {
        updates.push(`${key} = ?`);
        values.push(value);
      }
    }

    if (updates.length === 0) return User.findById(id);

    updates.push("updated_at = datetime('now')");
    values.push(id);

    const stmt = db.prepare(`UPDATE users SET ${updates.join(", ")} WHERE id = ?`);
    stmt.run(...values);

    return User.findById(id);
  },

  verifyPassword(user, password) {
    return bcrypt.compareSync(password, user.password_hash);
  },

  delete(id) {
    // Validate the id parameter - basic UUID format check
    if (!/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(id)) {
      throw new Error("Invalid user ID");
    }

    // Use a transaction to ensure atomicity
    db.exec("BEGIN TRANSACTION");
    try {
      // First delete all tasks created by or assigned to this user
      const taskStmt = db.prepare("DELETE FROM tasks WHERE created_by = ? OR assignee_id = ?");
      taskStmt.run(id, id);

      // Then delete the user
      const userStmt = db.prepare("DELETE FROM users WHERE id = ?");
      const result = userStmt.run(id);

      db.exec("COMMIT");
      return result.changes > 0; // Return true if user was deleted
    } catch (err) {
      db.exec("ROLLBACK");
      throw err;
    }
  },
};

module.exports = User;
