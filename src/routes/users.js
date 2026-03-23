const express = require("express");
const router = express.Router();
const userController = require("../controllers/userController");
const { authenticate } = require("../middleware/auth");

// All user routes require authentication
router.use(authenticate);

router.get("/", userController.list);
router.get("/:id", userController.get);
router.patch("/:id", userController.update);
router.delete("/:id", userController.deleteAccount);

module.exports = router;
