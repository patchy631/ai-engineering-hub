import asyncio
import httpx
import os
import io
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, List, Union, Any, Coroutine, TypeVar
from urllib.parse import urljoin

from llama_cloud.types import ReportMetadata
from llama_cloud_services.report.report import ReportClient

T = TypeVar("T")


class LlamaReport:
    """Client for managing reports and general report operations."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        project_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[int] = None,
        async_httpx_client: Optional[httpx.AsyncClient] = None,
    ):
        self.api_key = api_key or os.getenv("LLAMA_CLOUD_API_KEY", None)
        if not self.api_key:
            raise ValueError("No API key provided.")

        self.base_url = base_url or os.getenv(
            "LLAMA_CLOUD_BASE_URL", "https://api.cloud.llamaindex.ai"
        )
        self.timeout = timeout or 60

        # Initialize HTTP clients
        self._aclient = async_httpx_client or httpx.AsyncClient(timeout=self.timeout)

        # Set auth headers
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
        }

        self.organization_id = organization_id
        self.project_id = project_id
        self._client_params = {
            "timeout": self._aclient.timeout,
            "headers": self._aclient.headers,
            "base_url": self._aclient.base_url,
            "auth": self._aclient.auth,
            "event_hooks": self._aclient.event_hooks,
            "cookies": self._aclient.cookies,
            "max_redirects": self._aclient.max_redirects,
            "params": self._aclient.params,
            "trust_env": self._aclient.trust_env,
        }
        self._thread_pool = ThreadPoolExecutor(
            max_workers=min(10, (os.cpu_count() or 1) + 4)
        )

    @property
    def aclient(self) -> httpx.AsyncClient:
        if self._aclient is None:
            self._aclient = httpx.AsyncClient(**self._client_params)
        return self._aclient

    def _run_sync(self, coro: Coroutine[Any, Any, T]) -> T:
        """Run coroutine in a separate thread to avoid event loop issues"""

        # force a new client for this thread/event loop
        original_client = self._aclient
        self._aclient = None

        def run_coro() -> T:
            async def wrapped_coro() -> T:
                return await coro

            return asyncio.run(wrapped_coro())

        result = self._thread_pool.submit(run_coro).result()

        # restore the original client
        self._aclient = original_client

        return result

    async def _get_default_project(self) -> str:
        response = await self.aclient.get(
            urljoin(str(self.base_url), "/api/v1/projects"), headers=self.headers
        )
        response.raise_for_status()
        projects = response.json()
        default_project = [p for p in projects if p.get("is_default")]
        return default_project[0]["id"]

    async def _build_url(
        self, endpoint: str, extra_params: Optional[List[str]] = None
    ) -> str:
        """Helper method to build URLs with common query parameters."""
        url = urljoin(str(self.base_url), endpoint)

        if not self.project_id:
            self.project_id = await self._get_default_project()

        query_params = []
        if self.organization_id:
            query_params.append(f"organization_id={self.organization_id}")
        if self.project_id:
            query_params.append(f"project_id={self.project_id}")
        if extra_params:
            query_params.extend([p for p in extra_params if p is not None])

        if query_params:
            url += "?" + "&".join(query_params)

        return url

    async def acreate_report(
        self,
        name: str,
        template_instructions: Optional[str] = None,
        template_text: Optional[str] = None,
        template_file: Optional[Union[str, tuple[str, bytes]]] = None,
        input_files: Optional[List[Union[str, tuple[str, bytes]]]] = None,
        existing_retriever_id: Optional[str] = None,
    ) -> ReportClient:
        """Create a new report asynchronously."""
        url = await self._build_url("/api/v1/reports/")
        open_files: List[io.BufferedReader] = []

        data = {"name": name}
        if template_instructions:
            data["template_instructions"] = template_instructions
        if template_text:
            data["template_text"] = template_text
        if existing_retriever_id:
            data["existing_retriever_id"] = str(existing_retriever_id)

        files: List[tuple[str, io.BufferedReader | bytes]] = []
        if template_file:
            if isinstance(template_file, str):
                open_files.append(open(template_file, "rb"))
                files.append(("template_file", open_files[-1]))
            else:
                files.append(("template_file", template_file[1]))

        if input_files:
            for f in input_files:
                if isinstance(f, str):
                    open_files.append(open(f, "rb"))
                    files.append(("files", open_files[-1]))
                else:
                    files.append(("files", f[1]))

        response = await self.aclient.post(
            url, headers=self.headers, data=data, files=files
        )
        try:
            response.raise_for_status()
            report_id = response.json()["id"]
            return ReportClient(report_id, name, self)
        except httpx.HTTPStatusError as e:
            raise ValueError(
                f"Failed to create report: {e.response.text}\nError Code: {e.response.status_code}"
            )
        finally:
            for open_file in open_files:
                open_file.close()

    def create_report(
        self,
        name: str,
        template_instructions: Optional[str] = None,
        template_text: Optional[str] = None,
        template_file: Optional[Union[str, tuple[str, bytes]]] = None,
        input_files: Optional[List[Union[str, tuple[str, bytes]]]] = None,
        existing_retriever_id: Optional[str] = None,
    ) -> ReportClient:
        """Create a new report."""
        return self._run_sync(
            self.acreate_report(
                name=name,
                template_instructions=template_instructions,
                template_text=template_text,
                template_file=template_file,
                input_files=input_files,
                existing_retriever_id=existing_retriever_id,
            )
        )

    async def alist_reports(
        self, state: Optional[str] = None, limit: int = 100, offset: int = 0
    ) -> List[ReportClient]:
        """List all reports asynchronously."""
        params = []
        if state:
            params.append(f"state={state}")
        if limit:
            params.append(f"limit={limit}")
        if offset:
            params.append(f"offset={offset}")

        url = await self._build_url(
            "/api/v1/reports/list",
            extra_params=params,
        )

        response = await self.aclient.get(url, headers=self.headers)
        response.raise_for_status()
        data = response.json()

        return [
            ReportClient(r["report_id"], r["name"], self)
            for r in data["report_responses"]
        ]

    def list_reports(
        self, state: Optional[str] = None, limit: int = 100, offset: int = 0
    ) -> List[ReportClient]:
        """Synchronous wrapper for listing reports."""
        return self._run_sync(self.alist_reports(state, limit, offset))

    async def aget_report(self, report_id: str) -> ReportClient:
        """Get a Report instance for working with a specific report."""
        url = await self._build_url(f"/api/v1/reports/{report_id}")

        response = await self.aclient.get(url, headers=self.headers)
        response.raise_for_status()
        data = response.json()

        return ReportClient(data["report_id"], data["name"], self)

    def get_report(self, report_id: str) -> ReportClient:
        """Synchronous wrapper for getting a report."""
        return self._run_sync(self.aget_report(report_id))

    async def aget_report_metadata(self, report_id: str) -> ReportMetadata:
        """Get metadata for a specific report asynchronously.

        Returns:
            dict containing:
            - id: Report ID
            - name: Report name
            - state: Current report state
            - report_metadata: Additional metadata
            - template_file: Name of template file if used
            - template_instructions: Template instructions if provided
            - input_files: List of input file names
        """
        url = await self._build_url(f"/api/v1/reports/{report_id}/metadata")

        response = await self.aclient.get(url, headers=self.headers)
        response.raise_for_status()
        return ReportMetadata(**response.json())

    def get_report_metadata(self, report_id: str) -> ReportMetadata:
        """Synchronous wrapper for getting report metadata."""
        return self._run_sync(self.aget_report_metadata(report_id))

    async def adelete_report(self, report_id: str) -> None:
        """Delete a specific report asynchronously."""
        url = await self._build_url(f"/api/v1/reports/{report_id}")

        response = await self.aclient.delete(url, headers=self.headers)
        response.raise_for_status()

    def delete_report(self, report_id: str) -> None:
        """Synchronous wrapper for deleting a report."""
        return self._run_sync(self.adelete_report(report_id))
