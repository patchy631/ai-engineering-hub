# TaskFlow API

A lightweight task management API for small teams. Built with Express.js and SQLite.

## Features

- User authentication (register, login, JWT tokens)
- Task CRUD with status tracking (todo, in_progress, review, done)
- Priority levels (p0-p3)
- Task assignment to team members
- User profiles with task statistics

## Setup

```bash
cp .env.example .env
npm install
mkdir -p data
npm run dev
```

## API Endpoints

### Auth
- `POST /api/auth/register` - Create account
- `POST /api/auth/login` - Get token
- `GET /api/auth/me` - Current user (authenticated)

### Tasks
- `GET /api/tasks` - List tasks (filterable by status, assignee)
- `GET /api/tasks/:id` - Get task
- `POST /api/tasks` - Create task
- `PATCH /api/tasks/:id` - Update task
- `DELETE /api/tasks/:id` - Delete task

### Users
- `GET /api/users` - List users
- `GET /api/users/:id` - Get user with task stats
- `PATCH /api/users/:id` - Update profile

## Tech Stack

- **Runtime:** Node.js
- **Framework:** Express.js
- **Database:** SQLite (via better-sqlite3)
- **Auth:** JWT (jsonwebtoken + bcryptjs)
- **Testing:** Jest + Supertest
