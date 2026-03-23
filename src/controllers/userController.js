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
};

module.exports = userController;
