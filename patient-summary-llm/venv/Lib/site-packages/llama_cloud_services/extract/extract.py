import asyncio
import os
import time
from io import BufferedIOBase, BufferedReader, BytesIO
from pathlib import Path
from typing import List, Optional, Type, Union, Coroutine, Any, TypeVar
import warnings
import httpx
from pydantic import BaseModel
from llama_cloud import (
    ExtractAgent as CloudExtractAgent,
    ExtractAgentCreate,
    ExtractConfig,
    ExtractJob,
    ExtractJobCreate,
    ExtractRun,
    ExtractSchemaValidateRequest,
    ExtractAgentUpdate,
    File,
    ExtractMode,
    StatusEnum,
    Project,
    ExtractTarget,
    LlamaExtractSettings,
)
from llama_cloud.client import AsyncLlamaCloud
from llama_cloud_services.extract.utils import JSONObjectType, augment_async_errors
from llama_index.core.schema import BaseComponent
from llama_index.core.async_utils import run_jobs
from llama_index.core.bridge.pydantic import Field, PrivateAttr
from llama_index.core.constants import DEFAULT_BASE_URL
from concurrent.futures import ThreadPoolExecutor

T = TypeVar("T")

FileInput = Union[str, Path, bytes, BufferedIOBase]
SchemaInput = Union[JSONObjectType, Type[BaseModel]]

DEFAULT_EXTRACT_CONFIG = ExtractConfig(
    extraction_target=ExtractTarget.PER_DOC,
    extraction_mode=ExtractMode.ACCURATE,
)


class ExtractionAgent:
    """Class representing a single extraction agent with methods for extraction operations."""

    def __init__(
        self,
        client: AsyncLlamaCloud,
        agent: CloudExtractAgent,
        project_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        check_interval: int = 1,
        max_timeout: int = 2000,
        num_workers: int = 4,
        show_progress: bool = True,
        verbose: bool = False,
    ):
        self._client = client
        self._agent = agent
        self._project_id = project_id
        self._organization_id = organization_id
        self.check_interval = check_interval
        self.max_timeout = max_timeout
        self.num_workers = num_workers
        self.show_progress = show_progress
        self._verbose = verbose
        self._data_schema: Union[JSONObjectType, None] = None
        self._config: Union[ExtractConfig, None] = None
        self._thread_pool = ThreadPoolExecutor(
            max_workers=min(10, (os.cpu_count() or 1) + 4)
        )

    def _run_in_thread(self, coro: Coroutine[Any, Any, T]) -> T:
        """Run coroutine in a separate thread to avoid event loop issues"""

        def run_coro() -> T:
            async def wrapped_coro() -> T:
                async with httpx.AsyncClient(
                    timeout=self._client._client_wrapper.httpx_client.timeout,
                ) as client:
                    original_client = self._client._client_wrapper.httpx_client
                    self._client._client_wrapper.httpx_client = client
                    try:
                        return await coro
                    finally:
                        self._client._client_wrapper.httpx_client = original_client

            return asyncio.run(wrapped_coro())

        return self._thread_pool.submit(run_coro).result()

    @property
    def id(self) -> str:
        return self._agent.id

    @property
    def name(self) -> str:
        return self._agent.name

    @property
    def data_schema(self) -> dict:
        return self._agent.data_schema if not self._data_schema else self._data_schema

    @data_schema.setter
    def data_schema(self, data_schema: SchemaInput) -> None:
        processed_schema: JSONObjectType
        if isinstance(data_schema, dict):
            # TODO: if we expose a get_validated JSON schema method, we can use it here
            processed_schema = data_schema  # type: ignore
        elif isinstance(data_schema, type) and issubclass(data_schema, BaseModel):
            processed_schema = data_schema.model_json_schema()
        else:
            raise ValueError(
                "data_schema must be either a dictionary or a Pydantic model"
            )
        validated_schema = self._run_in_thread(
            self._client.llama_extract.validate_extraction_schema(
                request=ExtractSchemaValidateRequest(data_schema=processed_schema)
            )
        )
        self._data_schema = validated_schema.data_schema

    @property
    def config(self) -> ExtractConfig:
        return self._agent.config if not self._config else self._config

    @config.setter
    def config(self, config: ExtractConfig) -> None:
        self._config = config

    async def _upload_file(self, file_input: FileInput) -> File:
        """Upload a file for extraction."""
        if isinstance(file_input, BufferedIOBase):
            upload_file = file_input
        elif isinstance(file_input, bytes):
            upload_file = BytesIO(file_input)
        elif isinstance(file_input, (str, Path)):
            upload_file = open(file_input, "rb")
        else:
            raise ValueError(
                "file_input must be either a file path string, file bytes, or buffer object"
            )

        try:
            return await self._client.files.upload_file(
                project_id=self._project_id, upload_file=upload_file
            )
        finally:
            if isinstance(upload_file, BufferedReader):
                upload_file.close()

    async def _wait_for_job_result(self, job_id: str) -> Optional[ExtractRun]:
        """Wait for and return the results of an extraction job."""
        start = time.perf_counter()
        tries = 0
        while True:
            await asyncio.sleep(self.check_interval)
            tries += 1
            job = await self._client.llama_extract.get_job(
                job_id=job_id,
            )

            if job.status == StatusEnum.SUCCESS:
                return await self._client.llama_extract.get_run_by_job_id(
                    job_id=job_id,
                )
            elif job.status == StatusEnum.PENDING:
                end = time.perf_counter()
                if end - start > self.max_timeout:
                    raise Exception(f"Timeout while extracting the file: {job_id}")
                if self._verbose and tries % 10 == 0:
                    print(".", end="", flush=True)
                continue
            else:
                warnings.warn(
                    f"Failure in job: {job_id}, status: {job.status}, error: {job.error}"
                )
                return await self._client.llama_extract.get_run_by_job_id(
                    job_id=job_id,
                )

    def save(self) -> None:
        """Persist the extraction agent's schema and config to the database.

        Returns:
            ExtractionAgent: The updated extraction agent
        """
        self._agent = self._run_in_thread(
            self._client.llama_extract.update_extraction_agent(
                extraction_agent_id=self.id,
                request=ExtractAgentUpdate(
                    data_schema=self.data_schema,
                    config=self.config,
                ),
            )
        )

    async def _queue_extraction_test(
        self,
        files: Union[FileInput, List[FileInput]],
        extract_settings: LlamaExtractSettings,
    ) -> Union[ExtractJob, List[ExtractJob]]:
        if not isinstance(files, list):
            files = [files]
            single_file = True
        else:
            single_file = False

        upload_tasks = [self._upload_file(file) for file in files]
        with augment_async_errors():
            uploaded_files = await run_jobs(
                upload_tasks,
                workers=self.num_workers,
                desc="Uploading files",
                show_progress=self.show_progress,
            )

        async def run_job(file: File) -> ExtractRun:
            job_queued = await self._client.llama_extract.run_job_test_user(
                job_create=ExtractJobCreate(
                    extraction_agent_id=self.id,
                    file_id=file.id,
                    data_schema_override=self.data_schema,
                    config_override=self.config,
                ),
                extract_settings=extract_settings,
            )
            return await self._wait_for_job_result(job_queued.id)

        job_tasks = [run_job(file) for file in uploaded_files]
        with augment_async_errors():
            extract_jobs = await run_jobs(
                job_tasks,
                workers=self.num_workers,
                desc="Running extraction jobs",
                show_progress=self.show_progress,
            )

        if self._verbose:
            for file, job in zip(files, extract_jobs):
                file_repr = (
                    str(file) if isinstance(file, (str, Path)) else "<bytes/buffer>"
                )
                print(
                    f"Queued file extraction for file {file_repr} under job_id {job.id}"
                )

        return extract_jobs[0] if single_file else extract_jobs

    async def queue_extraction(
        self,
        files: Union[FileInput, List[FileInput]],
    ) -> Union[ExtractJob, List[ExtractJob]]:
        """
        Queue multiple files for extraction.

        Args:
            files (Union[FileInput, List[FileInput]]): The files to extract

        Returns:
            Union[ExtractJob, List[ExtractJob]]: The queued extraction jobs
        """
        """Queue one or more files for extraction concurrently."""
        if not isinstance(files, list):
            files = [files]
            single_file = True
        else:
            single_file = False

        upload_tasks = [self._upload_file(file) for file in files]
        with augment_async_errors():
            uploaded_files = await run_jobs(
                upload_tasks,
                workers=self.num_workers,
                desc="Uploading files",
                show_progress=self.show_progress,
            )

        job_tasks = [
            self._client.llama_extract.run_job(
                request=ExtractJobCreate(
                    extraction_agent_id=self.id,
                    file_id=file.id,
                    data_schema_override=self.data_schema,
                    config_override=self.config,
                ),
            )
            for file in uploaded_files
        ]
        with augment_async_errors():
            extract_jobs = await run_jobs(
                job_tasks,
                workers=self.num_workers,
                desc="Creating extraction jobs",
                show_progress=self.show_progress,
            )

        if self._verbose:
            for file, job in zip(files, extract_jobs):
                file_repr = (
                    str(file) if isinstance(file, (str, Path)) else "<bytes/buffer>"
                )
                print(
                    f"Queued file extraction for file {file_repr} under job_id {job.id}"
                )

        return extract_jobs[0] if single_file else extract_jobs

    async def aextract(
        self, files: Union[FileInput, List[FileInput]]
    ) -> Union[ExtractRun, List[ExtractRun]]:
        """Asynchronously extract data from one or more files using this agent.

        Args:
            files (Union[FileInput, List[FileInput]]): The files to extract

        Returns:
            Union[ExtractRun, List[ExtractRun]]: The extraction results
        """
        if not isinstance(files, list):
            files = [files]
            single_file = True
        else:
            single_file = False

        # Queue all files for extraction
        jobs = await self.queue_extraction(files)
        # Wait for all results concurrently
        result_tasks = [self._wait_for_job_result(job.id) for job in jobs]
        with augment_async_errors():
            results = await run_jobs(
                result_tasks,
                workers=self.num_workers,
                desc="Extracting files",
                show_progress=self.show_progress,
            )

        return results[0] if single_file else results

    def extract(
        self, files: Union[FileInput, List[FileInput]]
    ) -> Union[ExtractRun, List[ExtractRun]]:
        """Synchronously extract data from one or more files using this agent.

        Args:
            files (Union[FileInput, List[FileInput]]): The files to extract

        Returns:
            Union[ExtractRun, List[ExtractRun]]: The extraction results
        """
        return self._run_in_thread(self.aextract(files))

    def get_extraction_job(self, job_id: str) -> ExtractJob:
        """
        Get the extraction job for a given job_id.

        Args:
            job_id (str): The job_id to get the extraction job for

        Returns:
            ExtractJob: The extraction job
        """
        return self._run_in_thread(self._client.llama_extract.get_job(job_id=job_id))

    def get_extraction_run_for_job(self, job_id: str) -> ExtractRun:
        """
        Get the extraction run for a given job_id.

        Args:
            job_id (str): The job_id to get the extraction run for

        Returns:
            ExtractRun: The extraction run
        """
        return self._run_in_thread(
            self._client.llama_extract.get_run_by_job_id(
                job_id=job_id,
            )
        )

    def list_extraction_runs(self) -> List[ExtractRun]:
        """List extraction runs for the extraction agent.

        Returns:
            List[ExtractRun]: List of extraction runs
        """
        return self._run_in_thread(
            self._client.llama_extract.list_extract_runs(
                extraction_agent_id=self.id,
            )
        )

    def __repr__(self) -> str:
        return f"ExtractionAgent(id={self.id}, name={self.name})"


class LlamaExtract(BaseComponent):
    """Factory class for creating and managing extraction agents."""

    api_key: str = Field(description="The API key for the LlamaExtract API.")
    base_url: str = Field(description="The base URL of the LlamaExtract API.")
    check_interval: int = Field(
        default=1,
        description="The interval in seconds to check if the extraction is done.",
    )
    max_timeout: int = Field(
        default=2000,
        description="The maximum timeout in seconds to wait for the extraction to finish.",
    )
    num_workers: int = Field(
        default=4,
        gt=0,
        lt=10,
        description="The number of workers to use sending API requests for extraction.",
    )
    show_progress: bool = Field(
        default=True, description="Show progress when extracting multiple files."
    )
    verbose: bool = Field(
        default=False, description="Show verbose output when extracting files."
    )
    _async_client: AsyncLlamaCloud = PrivateAttr()
    _thread_pool: ThreadPoolExecutor = PrivateAttr()
    _project_id: Optional[str] = PrivateAttr()
    _organization_id: Optional[str] = PrivateAttr()

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        check_interval: int = 1,
        max_timeout: int = 2000,
        num_workers: int = 4,
        show_progress: bool = True,
        project_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        verbose: bool = False,
    ):
        if not api_key:
            api_key = os.getenv("LLAMA_CLOUD_API_KEY", None)
            if api_key is None:
                raise ValueError("The API key is required.")

        if not base_url:
            base_url = os.getenv("LLAMA_CLOUD_BASE_URL", None) or DEFAULT_BASE_URL

        super().__init__(
            api_key=api_key,
            base_url=base_url,
            check_interval=check_interval,
            max_timeout=max_timeout,
            num_workers=num_workers,
            show_progress=show_progress,
            verbose=verbose,
        )

        self._async_client = AsyncLlamaCloud(
            token=self.api_key, base_url=self.base_url, timeout=None
        )
        self._thread_pool = ThreadPoolExecutor(
            max_workers=min(10, (os.cpu_count() or 1) + 4)
        )
        # Fetch default project id if not provided
        if not project_id:
            project_id = os.getenv("LLAMA_CLOUD_PROJECT_ID", None)
            if not project_id:
                print("No project_id provided, fetching default project.")
                projects: List[Project] = self._run_in_thread(
                    self._async_client.projects.list_projects()
                )
                default_project = [p for p in projects if p.is_default]
                if not default_project:
                    raise ValueError(
                        "No default project found. Please provide a project_id."
                    )
                project_id = default_project[0].id

        self._project_id = project_id
        self._organization_id = organization_id

    def _run_in_thread(self, coro: Coroutine[Any, Any, T]) -> T:
        """Run coroutine in a separate thread to avoid event loop issues"""

        def run_coro() -> T:
            # Create a new client for this thread
            async def wrapped_coro() -> T:
                async with httpx.AsyncClient(
                    timeout=self._async_client._client_wrapper.httpx_client.timeout,
                ) as client:
                    # Replace the client in the coro's context
                    original_client = self._async_client._client_wrapper.httpx_client
                    self._async_client._client_wrapper.httpx_client = client
                    try:
                        return await coro
                    finally:
                        self._async_client._client_wrapper.httpx_client = (
                            original_client
                        )

            return asyncio.run(wrapped_coro())

        return self._thread_pool.submit(run_coro).result()

    def create_agent(
        self,
        name: str,
        data_schema: SchemaInput,
        config: Optional[ExtractConfig] = None,
    ) -> ExtractionAgent:
        """Create a new extraction agent.

        Args:
            name (str): The name of the extraction agent
            data_schema (SchemaInput): The data schema for the extraction agent
            config (Optional[ExtractConfig]): The extraction config for the agent

        Returns:
            ExtractionAgent: The created extraction agent
        """

        if isinstance(data_schema, dict):
            data_schema = data_schema
        elif issubclass(data_schema, BaseModel):
            data_schema = data_schema.model_json_schema()
        else:
            raise ValueError(
                "data_schema must be either a dictionary or a Pydantic model"
            )

        agent = self._run_in_thread(
            self._async_client.llama_extract.create_extraction_agent(
                project_id=self._project_id,
                organization_id=self._organization_id,
                request=ExtractAgentCreate(
                    name=name,
                    data_schema=data_schema,
                    config=config or DEFAULT_EXTRACT_CONFIG,
                ),
            )
        )

        return ExtractionAgent(
            client=self._async_client,
            agent=agent,
            project_id=self._project_id,
            organization_id=self._organization_id,
            check_interval=self.check_interval,
            max_timeout=self.max_timeout,
            num_workers=self.num_workers,
            show_progress=self.show_progress,
            verbose=self.verbose,
        )

    def get_agent(
        self,
        name: Optional[str] = None,
        id: Optional[str] = None,
    ) -> ExtractionAgent:
        """Get extraction agents by name or extraction agent ID.

        Args:
            name (Optional[str]): Filter by name
            extraction_agent_id (Optional[str]): Filter by extraction agent ID

        Returns:
            ExtractionAgent: The extraction agent
        """
        if id is not None and name is not None:
            warnings.warn(
                "Both name and extraction_agent_id are provided. Using extraction_agent_id."
            )

        if id:
            agent = self._run_in_thread(
                self._async_client.llama_extract.get_extraction_agent(
                    extraction_agent_id=id,
                )
            )

        elif name:
            agent = self._run_in_thread(
                self._async_client.llama_extract.get_extraction_agent_by_name(
                    name=name,
                    project_id=self._project_id,
                )
            )
        else:
            raise ValueError("Either name or extraction_agent_id must be provided.")

        return ExtractionAgent(
            client=self._async_client,
            agent=agent,
            project_id=self._project_id,
            organization_id=self._organization_id,
            check_interval=self.check_interval,
            max_timeout=self.max_timeout,
            num_workers=self.num_workers,
            show_progress=self.show_progress,
            verbose=self.verbose,
        )

    def list_agents(self) -> List[ExtractionAgent]:
        """List all available extraction agents."""
        agents = self._run_in_thread(
            self._async_client.llama_extract.list_extraction_agents(
                project_id=self._project_id,
            )
        )

        return [
            ExtractionAgent(
                client=self._async_client,
                agent=agent,
                project_id=self._project_id,
                organization_id=self._organization_id,
                check_interval=self.check_interval,
                max_timeout=self.max_timeout,
                num_workers=self.num_workers,
                show_progress=self.show_progress,
                verbose=self.verbose,
            )
            for agent in agents
        ]

    def delete_agent(self, agent_id: str) -> None:
        """Delete an extraction agent by ID.

        Args:
            agent_id (str): ID of the extraction agent to delete
        """
        self._run_in_thread(
            self._async_client.llama_extract.delete_extraction_agent(
                extraction_agent_id=agent_id
            )
        )


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    data_dir = Path(__file__).parent.parent / "tests" / "data"
    extractor = LlamaExtract()
    try:
        agent = extractor.get_agent(name="test-agent")
    except Exception:
        agent = extractor.create_agent(
            "test-agent",
            {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "summary": {"type": "string"},
                },
            },
        )
    results = agent.extract(data_dir / "slide" / "conocophilips.pdf")
    extractor.delete_agent(agent.id)
    print(results)
