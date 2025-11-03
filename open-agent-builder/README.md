# Open Agent Builder (with Composio)

> **Note:** This project is actually a fork of [Open Agent Builder](https://github.com/firecrawl/open-agent-builder) released by [Firecrawl](https://firecrawl.dev) team. Some features are still very new and we welcome contributions and PRs!

The application is a visual workflow builder for creating AI agent pipelines powered by [Composio's](https://composio.dev/) 10,000 + tools integration making a skill layer for your AI agents. You essentially build complex agent workflows with a drag-and-drop interface, then execute them with real-time streaming updates.

How It Works:

1. **Drag-and-drop interface** for building agent workflows
2. **Real-time execution** with streaming updates
3. **8 core node types**: Start, Agent, Tools, Transform, If/Else, While Loop, User Approval, End
4. **MCP protocol support** for extensible tool integration using Composio

We use:

| Technology                                                 | Purpose                                                                                                 |
| ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| **[Composio](https://composio.dev)**                       | 10,000 + tools integration making a skill layer for your AI agents                                      |
| **[Next.js 16 (canary)](https://nextjs.org/)**             | React framework with App Router for frontend and API routes                                             |
| **[TypeScript](https://www.typescriptlang.org/)**          | Type-safe development across the stack                                                                  |
| **[LangGraph](https://github.com/langchain-ai/langgraph)** | Workflow orchestration engine with state management, conditional routing, and human-in-the-loop support |
| **[Convex](https://convex.dev)**                           | Real-time database with automatic reactivity for workflows, executions, and user data                   |
| **[Clerk](https://clerk.com)**                             | Authentication and user management with JWT integration                                                 |
| **[Tailwind CSS](https://tailwindcss.com/)**               | Utility-first CSS framework for responsive UI                                                           |
| **[React Flow](https://reactflow.dev/)**                   | Visual workflow builder canvas with drag-and-drop nodes                                                 |
| **[Anthropic](https://www.anthropic.com/)**                | Claude AI integration with native MCP support (Claude Haiku 4.5 & Sonnet 4.5)                           |
| **[OpenAI](https://platform.openai.com/)**                 | gpt-5 integration                                                                                       |
| **[Groq](https://groq.com/)**                              | Fast inference for open models                                                                          |
| **[E2B](https://e2b.dev)**                                 | Sandboxed code execution for secure transform nodes

## Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/patchy631/ai-engineering-hub.git
cd ai-engineering-hub/open-agent-builder
npm install
```

### 2. Set Up Convex (Database)

Convex handles all workflow and execution data persistence.

```bash
# Install Convex CLI globally
npm install -g convex

# Initialize Convex project
npx convex dev
```

This will:

- Open your browser to create/link a Convex project
- Generate a `NEXT_PUBLIC_CONVEX_URL` in your `.env.local`
- Start the Convex development server

Keep the Convex dev server running in a separate terminal.

### 3. Set Up Clerk (Authentication)

Clerk provides secure user authentication and management.

1. Go to [clerk.com](https://clerk.com) and create a new application
2. In your Clerk dashboard:
   - Go to **API Keys**
   - Copy your keys
3. Go to **JWT Templates** → **Convex**:
   - Click "Apply"
   - Copy the issuer URL

Add to your `.env.local`:

```bash
# Clerk Authentication
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...

# Clerk + Convex Integration
CLERK_JWT_ISSUER_DOMAIN=https://your-clerk-domain.clerk.accounts.dev
```

### 4. Configure Convex Authentication

Edit `convex/auth.config.ts` and update the domain:

```typescript
export default {
  providers: [
    {
      domain: "https://your-clerk-domain.clerk.accounts.dev", // Your Clerk issuer URL
      applicationID: "convex",
    },
  ],
};
```

Then push the auth config to Convex:

```bash
npx convex dev
```

### 5. Optional: Configure Default LLM Provider

While users can add their own LLM API keys through the UI (Settings → API Keys), you can optionally set a default provider in `.env.local`:

```bash
# Anthropic Claude (Recommended - Native MCP support with Haiku 4.5 & Sonnet 4.5)
ANTHROPIC_API_KEY=sk-ant-...

# OpenAI GPT-5
OPENAI_API_KEY=sk-...

# Groq
GROQ_API_KEY=gsk_...
```

> **Important:** For workflows using MCP tools, Anthropic Claude is currently the recommended provider as it has native MCP support.

### 6. Optional: E2B Code Interpreter

For advanced transform nodes with sandboxed code execution:

```bash
# E2B Code Interpreter (Optional)
E2B_API_KEY=e2b_...
```

Get your key at [e2b.dev](https://e2b.dev)

## Running the Application

```bash
# Terminal 1: Convex dev server
npx convex dev

# Terminal 2: Next.js dev server
npm run dev
```

Or run both with one command:

```bash
npm run dev:all
```

Visit [http://localhost:3000](http://localhost:3000)

## 📬 Stay Updated with Our Newsletter!

**Get a FREE Data Science eBook** 📖 with 150+ essential lessons in Data Science when you subscribe to our newsletter! Stay in the loop with the latest tutorials, insights, and exclusive resources. [Subscribe now!](https://join.dailydoseofds.com)

[![Daily Dose of Data Science Newsletter](https://github.com/patchy631/ai-engineering/blob/main/resources/join_ddods.png)](https://join.dailydoseofds.com)

## Contribution

Contributions are welcome! Feel free to fork this repository and submit pull requests with your improvements.
