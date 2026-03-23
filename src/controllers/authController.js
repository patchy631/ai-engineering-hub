const User = require("../models/User");
const { generateToken } = require("../middleware/auth");

const authController = {
  register(req, res, next) {
    try {
      const { email, name, password } = req.body;

      if (!email || !name || !password) {
        return res.status(400).json({ error: "Email, name, and password are required" });
      }

      if (password.length < 8) {
        return res.status(400).json({ error: "Password must be at least 8 characters" });
      }

      const existing = User.findByEmail(email);
      if (existing) {
        return res.status(409).json({ error: "Email already registered" });
      }

      const user = User.create({ email, name, password });
      const token = generateToken(user);

      res.status(201).json({ user, token });
    } catch (err) {
      next(err);
    }
  },

  login(req, res, next) {
    try {
      const { email, password } = req.body;

      if (!email || !password) {
        return res.status(400).json({ error: "Email and password are required" });
      }

      const user = User.findByEmail(email);
      if (!user || !User.verifyPassword(user, password)) {
        return res.status(401).json({ error: "Invalid email or password" });
      }

      const token = generateToken({
        id: user.id,
        email: user.email,
        role: user.role,
      });

      res.json({
        user: { id: user.id, email: user.email, name: user.name, role: user.role },
        token,
      });
    } catch (err) {
      next(err);
    }
  },

  me(req, res, next) {
    try {
      const user = User.findById(req.user.id);
      if (!user) {
        return res.status(404).json({ error: "User not found" });
      }
      res.json({ user });
    } catch (err) {
      next(err);
    }
  },
};

module.exports = authController;
