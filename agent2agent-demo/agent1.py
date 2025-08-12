from python_a2a import A2AServer, skill, agent, run_server, TaskStatus, TaskState
import math
import re

@agent(
    name="Sine Agent",
    description="Provides the sine of a number",
    version="1.0.0"
)
class SineAgent(A2AServer):
    
    @skill(
        name="Get Sine",
        description="Get the sine of a number",
        tags=["sine", "sin"]
    )
    def get_sine(self, number):
        """Get the sine of a number."""
        # Mock implementation
        return f"The sine of {number} is {math.sin(number)}"
    
    def handle_task(self, task):
        # Extract location from message

        input_message = task.message["content"]["text"]

        # regex to extract the number from the text
        match = re.search(r"([-+]?[0-9]*\.?[0-9]+)", input_message)

        number = float(match.group(1))
        print("number", number)
        # Get weather and create response
        sine_output = self.get_sine(number)
        task.artifacts = [{
                "parts": [{"type": "text", "text": sine_output}]
            }]
        task.status = TaskStatus(state=TaskState.COMPLETED)

        return task

# Run the server
if __name__ == "__main__":
    agent = SineAgent()
    run_server(agent, port=4737)