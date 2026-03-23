const Task = require("../models/Task");

const taskController = {
  list(req, res, next) {
    try {
      const { status, assignee } = req.query;
      const tasks = Task.findAll({
        status,
        assigneeId: assignee,
      });
      res.json({ tasks });
    } catch (err) {
      next(err);
    }
  },

  get(req, res, next) {
    try {
      const task = Task.findById(req.params.id);
      if (!task) {
        return res.status(404).json({ error: "Task not found" });
      }
      res.json({ task });
    } catch (err) {
      next(err);
    }
  },

  create(req, res, next) {
    try {
      const { title, description, priority, assigneeId, dueDate } = req.body;

      if (!title) {
        return res.status(400).json({ error: "Title is required" });
      }

      const task = Task.create({
        title,
        description,
        priority,
        assigneeId,
        createdBy: req.user.id,
        dueDate,
      });

      res.status(201).json({ task });
    } catch (err) {
      next(err);
    }
  },

  update(req, res, next) {
    try {
      const existing = Task.findById(req.params.id);
      if (!existing) {
        return res.status(404).json({ error: "Task not found" });
      }

      const task = Task.update(req.params.id, req.body);
      res.json({ task });
    } catch (err) {
      if (err.message.startsWith("Invalid status") || err.message.startsWith("Invalid priority")) {
        return res.status(400).json({ error: err.message });
      }
      next(err);
    }
  },

  remove(req, res, next) {
    try {
      const existing = Task.findById(req.params.id);
      if (!existing) {
        return res.status(404).json({ error: "Task not found" });
      }

      Task.delete(req.params.id);
      res.status(204).send();
    } catch (err) {
      next(err);
    }
  },
};

module.exports = taskController;
