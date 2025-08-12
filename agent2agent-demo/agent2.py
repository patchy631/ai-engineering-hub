from python_a2a import A2AServer, skill, agent, run_server, TaskStatus, TaskState
import math
import re

@agent(
    name="Cosine Agent",
    description="Provides the cosine of a number",
    version="1.0.0"
)
class CosineAgent(A2AServer):
    
    @skill(
        name="Get Cos",
        description="Get the cosine of a number",
        tags=["cos", "cosine"]
    )
    def get_cosine(self, number):
        """Get the cosine of a number."""
        # Mock implementation
        return f"The cosine of {number} is {math.cos(number)}"
    
    def handle_task(self, task):
        # Extract location from message

        input_message = task.message["content"]["text"]

        # regex to extract the number from the text
        match = re.search(r"([-+]?[0-9]*\.?[0-9]+)", input_message)

        number = float(match.group(1))
        print("number", number)
        # Get weather and create response
        cosine_output = self.get_cosine(number)
        task.artifacts = [{
                "parts": [{"type": "text", "text": cosine_output}]
            }]
        task.status = TaskStatus(state=TaskState.COMPLETED)

        return task

# Run the server
if __name__ == "__main__":
    agent = CosineAgent()
    run_server(agent, port=4738)