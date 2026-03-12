import mindsdb_sdk

# connects to the default port (47334) on localhost
server = mindsdb_sdk.connect("http://127.0.0.1:47334")
agent = server.agents.get("sales_agent")

# stream the completion
completion = agent.completion_stream(
    [
        {
            "question": "Who is the top customer by revenue? Include their full name, job title, and company from our CRM.",
            "answer": None,
        }
    ]
)

# print the completion
for chunk in completion:
    print(chunk, end="", flush=True)
