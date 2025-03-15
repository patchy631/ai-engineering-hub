# custom client with custom model loader
# https://github.com/microsoft/autogen/blob/main/notebook/agentchat_custom_model.ipynb
# oai ModelClient: https://microsoft.github.io/autogen/docs/reference/oai/client/
# oai client source code: https://github.com/microsoft/autogen/blob/7c8d357e0cde527a3875cce4302906292e4b14be/autogen/oai/client.py#L4


from types import SimpleNamespace

from imagine.langchain import ImagineChat, ImagineLLM


class CustomModelClient:
    def __init__(self, config, **kwargs):
        print(f"CustomModelClient config: {config}")
        self.model_name = config["model"]

        # custom params for the ImagineLLM object
        gen_config_params = config.get("params", {})
        self.max_length = gen_config_params.get("max_length", 256)
        self.api_key = gen_config_params.get("api_key", None)
        self.verify = gen_config_params.get("verify", False)
        self.endpoint = gen_config_params.get("endpoint", None)
        self.temperature = gen_config_params.get("temperature", 0.7)

        # it works using the ImagineChat or ImagineLLM object for the model
        if self.model_name == "imagine":
            self.model = ImagineLLM(
                model="Llama-3.1-70B",
                max_tokens=self.max_length,
                api_key=self.api_key,
                verify=self.verify,
                endpoint=self.endpoint,
                temperature=self.temperature,
            )
        elif self.model_name == "imaginechat":
            self.model = ImagineChat(
                model="Llama-3.1-70B",
                max_tokens=self.max_length,
                api_key=self.api_key,
                verify=self.verify,
                endpoint=self.endpoint,
                temperature=self.temperature,
            )
        else:
            raise ValueError(f"{self.model_name}: not a valid model name")
        print(f"Loaded model {config['model']}")

    def create(self, params):
        if params.get("stream", False) and "messages" in params:
            raise NotImplementedError("Local models do not support streaming.")
        else:
            print("params :", params)
            num_of_responses = params.get("n", 1)

            # can create my own data response class
            # here using SimpleNamespace for simplicity

            response = SimpleNamespace()

            inputs = " ".join([item["content"] for item in params["messages"]])

            response.choices = []
            response.model = self.model_name

            for _ in range(num_of_responses):
                if self.model_name == "imagine" or self.model_name == "imaginechat":
                    text = self.model.invoke(inputs, max_tokens=self.max_length)
                else:
                    raise ValueError(f"{self.model_name}: not a valid model name")

                choice = SimpleNamespace()
                choice.message = SimpleNamespace()
                choice.message.content = text
                choice.message.tool_calls = None
                # if
                response.choices.append(choice)

            return response

    def message_retrieval(self, response):
        """Retrieve the messages from the response."""
        print("response: ", response)
        choices = response.choices
        messages = []
        for choice in choices:
            if hasattr(choice.message, "tool_calls") and choice.message.tool_calls:
                messages.append(choice.message.tool_calls)
            else:
                messages.append(choice.message.content)
        return messages

    def cost(self, response) -> float:
        """Calculate the cost of the response."""
        response.cost = 0
        return 0

    @staticmethod
    def get_usage(response):
        # returns a dict of prompt_tokens, completion_tokens, total_tokens, cost, model
        # if usage needs to be tracked, else None
        return {}