const request = require("supertest");
const app = require("../src/app");

describe("Task Endpoints", () => {
  let authToken;

  beforeAll(async () => {
    // Register a test user and get token
    const res = await request(app).post("/api/auth/register").send({
      email: `tasks-test-${Date.now()}@example.com`,
      name: "Task Tester",
      password: "password123",
    });
    authToken = res.body.token;
  });

  describe("GET /api/tasks", () => {
    it("should require authentication", async () => {
      const res = await request(app).get("/api/tasks");
      expect(res.status).toBe(401);
    });

    it("should return tasks for authenticated user", async () => {
      const res = await request(app)
        .get("/api/tasks")
        .set("Authorization", `Bearer ${authToken}`);

      expect(res.status).toBe(200);
      expect(res.body).toHaveProperty("tasks");
      expect(Array.isArray(res.body.tasks)).toBe(true);
    });
  });

  describe("POST /api/tasks", () => {
    it("should create a task", async () => {
      const res = await request(app)
        .post("/api/tasks")
        .set("Authorization", `Bearer ${authToken}`)
        .send({
          title: "Test Task",
          description: "A test task",
          priority: "p1",
        });

      expect(res.status).toBe(201);
      expect(res.body.task).toHaveProperty("id");
      expect(res.body.task.title).toBe("Test Task");
      expect(res.body.task.status).toBe("todo");
    });

    it("should reject tasks without a title", async () => {
      const res = await request(app)
        .post("/api/tasks")
        .set("Authorization", `Bearer ${authToken}`)
        .send({ description: "No title" });

      expect(res.status).toBe(400);
    });
  });

  describe("PATCH /api/tasks/:id", () => {
    it("should update task status", async () => {
      // Create a task first
      const created = await request(app)
        .post("/api/tasks")
        .set("Authorization", `Bearer ${authToken}`)
        .send({ title: "Update Me" });

      const res = await request(app)
        .patch(`/api/tasks/${created.body.task.id}`)
        .set("Authorization", `Bearer ${authToken}`)
        .send({ status: "in_progress" });

      expect(res.status).toBe(200);
      expect(res.body.task.status).toBe("in_progress");
    });

    it("should reject invalid status values", async () => {
      const created = await request(app)
        .post("/api/tasks")
        .set("Authorization", `Bearer ${authToken}`)
        .send({ title: "Bad Status" });

      const res = await request(app)
        .patch(`/api/tasks/${created.body.task.id}`)
        .set("Authorization", `Bearer ${authToken}`)
        .send({ status: "invalid_status" });

      expect(res.status).toBe(400);
    });
  });
});
