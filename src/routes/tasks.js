const express = require("express");
const router = express.Router();
const taskController = require("../controllers/taskController");
const { authenticate } = require("../middleware/auth");

// All task routes require authentication
router.use(authenticate);

router.get("/", taskController.list);
router.get("/:id", taskController.get);
router.post("/", taskController.create);
router.patch("/:id", taskController.update);
router.delete("/:id", taskController.remove);

module.exports = router;
