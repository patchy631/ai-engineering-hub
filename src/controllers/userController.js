const User = require("../models/User");
const Task = require("../models/Task");

const userController = {
  list(req, res, next) {
    try {
      const users = User.findAll();
      res.json({ users });
    } catch (err) {
      next(err);
    }
  },

  get(req, res, next) {
    try {
      const user = User.findById(req.params.id);
      if (!user) {
        return res.status(404).json({ error: "User not found" });
      }

      const taskStats = Task.countByUser(req.params.id);
      res.json({ user, taskStats });
    } catch (err) {
      next(err);
    }
  },

  update(req, res, next) {
    try {
      // Users can only update their own profile unless they're admin
      if (req.user.id !== req.params.id && req.user.role !== "admin") {
        return res.status(403).json({ error: "You can only update your own profile" });
      }

      const user = User.update(req.params.id, req.body);
      if (!user) {
        return res.status(404).json({ error: "User not found" });
      }

      res.json({ user });
    } catch (err) {
      next(err);
    }
  },

  deleteAccount(req, res, next) {
    try {
      // Users can only delete their own account unless they're admin
      if (req.user.id !== req.params.id && req.user.role !== "admin") {
        return res.status(403).json({ error: "You can only delete your own account" });
      }

      // Validate the id parameter - basic UUID format check
      if (!/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(req.params.id)) {
        return res.status(400).json({ error: "Invalid user ID" });
      }

      // Check if user exists first
      const user = User.findById(req.params.id);
      if (!user) {
        return res.status(404).json({ error: "User not found" });
      }

      // Check if the user is the last admin
      if (req.user.role === "admin" && user.role === "admin") {
        const allUsers = User.findAll();
        const admins = allUsers.filter(u => u.role === "admin");
        if (admins.length <= 1) {
          return res.status(403).json({ error: "Cannot delete the last admin account" });
        }
      }

      // Delete user and all their tasks
      const deleted = User.delete(req.params.id);
      if (!deleted) {
        return res.status(404).json({ error: "User not found" });
      }

      res.status(204).end();
    } catch (err) {
      next(err);
    }
  },
};

module.exports = userController;
