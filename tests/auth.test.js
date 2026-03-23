const request = require("supertest");
const app = require("../src/app");

describe("Auth Endpoints", () => {
  describe("POST /api/auth/register", () => {
    it("should register a new user", async () => {
      const res = await request(app).post("/api/auth/register").send({
        email: `test-${Date.now()}@example.com`,
        name: "Test User",
        password: "password123",
      });

      expect(res.status).toBe(201);
      expect(res.body.user).toHaveProperty("id");
      expect(res.body.user).toHaveProperty("email");
      expect(res.body).toHaveProperty("token");
    });

    it("should reject registration without required fields", async () => {
      const res = await request(app).post("/api/auth/register").send({
        email: "incomplete@example.com",
      });

      expect(res.status).toBe(400);
    });

    it("should reject short passwords", async () => {
      const res = await request(app).post("/api/auth/register").send({
        email: "short@example.com",
        name: "Short Pass",
        password: "123",
      });

      expect(res.status).toBe(400);
    });
  });

  describe("POST /api/auth/login", () => {
    it("should reject invalid credentials", async () => {
      const res = await request(app).post("/api/auth/login").send({
        email: "nobody@example.com",
        password: "wrongpassword",
      });

      expect(res.status).toBe(401);
    });
  });

  describe("GET /api/auth/me", () => {
    it("should reject unauthenticated requests", async () => {
      const res = await request(app).get("/api/auth/me");

      expect(res.status).toBe(401);
    });
  });
});
