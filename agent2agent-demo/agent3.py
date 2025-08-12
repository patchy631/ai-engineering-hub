from python_a2a import A2AServer, skill, agent, run_server, TaskStatus, TaskState
import math
import re

@agent(
    name="Tangent Agent",
    description="Provides the tangent of a number",
    version="1.0.0"
)
class TangentAgent(A2AServer):
    
    @skill(
        name="Get Tangent",
        description="Get the tangent of a number",
        tags=["tangent", "tan"]
    )
    def get_tangent(self, number):
        """Get the tangent of a number."""
        # Mock implementation
        return f"The tangent of {number} is {math.tan(number)}"
    
    def handle_task(self, task):
        # Extract location from message

        input_message = task.message["content"]["text"]

        # regex to extract the number from the text
        match = re.search(r"([-+]?[0-9]*\.?[0-9]+)", input_message)

        number = float(match.group(1))
        print("number", number)
        # Get weather and create response
        tangent_output = self.get_tangent(number)
        task.artifacts = [{
                "parts": [{"type": "text", "text": tangent_output}]
            }]
        task.status = TaskStatus(state=TaskState.COMPLETED)

        return task

# Run the server
if __name__ == "__main__":
    agent = TangentAgent()
    run_server(agent, port=4739)