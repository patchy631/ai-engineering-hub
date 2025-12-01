from llama_index.indices.managed.llama_cloud import LlamaCloudIndex
import llama_index.core
import os
from dotenv import load_dotenv

class LlamaCloudSetup:
    def __init__(self):
        load_dotenv()
        self.llama_cloud_api_key = os.getenv('LLAMA_CLOUD_API_KEY')
        self.phoenix_api_key = os.getenv('PHOENIX_API_KEY')
        
        self.index = LlamaCloudIndex(
            name="city_pdfs_index",
            project_name="Default",
            organization_id="8c1b26ae-5c98-4873-bce9-28d0c67a3dce",
            api_key=self.llama_cloud_api_key,
        )

        self._setup_observability()

    def _setup_observability(self):
        """Set up observability using Arize Phoenix."""
        os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = f"api_key={self.phoenix_api_key}"
        llama_index.core.set_global_handler(
            "arize_phoenix", endpoint="https://llamatrace.com/v1/traces"
        )

    def get_query_engine(self):
        """Returns the query engine instance."""
        return self.index.as_query_engine()


# Usage example:
if __name__ == "__main__":
    llama_cloud_setup = LlamaCloudSetup()
    query_engine = llama_cloud_setup.get_query_engine()
