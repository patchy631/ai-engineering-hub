import asyncio
import httpx
import time
from typing import Optional, List, Literal, Union, TYPE_CHECKING
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from llama_cloud.types import (
    ReportEventItemEventData_Progress,
    ReportMetadata,
    EditSuggestion,
    ReportResponse,
    ReportPlan,
    ReportBlock,
    ReportPlanBlock,
    Report,
)

if TYPE_CHECKING:
    from llama_cloud_services.report.base import LlamaReport


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class Message:
    role: MessageRole
    content: str
    timestamp: datetime


@dataclass
class EditAction:
    block_idx: int
    old_content: str
    new_content: Optional[str]
    action: Literal["approved", "rejected"]
    timestamp: datetime


DEFAULT_POLL_INTERVAL = 5
DEFAULT_TIMEOUT = 600


class ReportClient:
    """Client for operations on a specific report."""

    def __init__(self, report_id: str, name: str, parent_client: "LlamaReport"):
        self.report_id = report_id
        self.name = name
        self._client = parent_client
        self._headers = parent_client.headers
        self._run_sync = parent_client._run_sync
        self._build_url = parent_client._build_url
        self.chat_history: List[Message] = []
        self.edit_history: List[EditAction] = []

    @property
    def aclient(self) -> httpx.AsyncClient:
        return self._client.aclient

    def __str__(self) -> str:
        return f"Report(id={self.report_id}, name={self.name})"

    def __repr__(self) -> str:
        return f"Report(id={self.report_id}, name={self.name})"

    def _get_block_content(self, block: Union[ReportBlock, ReportPlanBlock]) -> str:
        if isinstance(block, ReportBlock):
            return block.template
        elif isinstance(block, ReportPlanBlock):
            return block.block.template
        else:
            raise ValueError(f"Invalid block type: {type(block)}")

    def _get_block_idx(self, block: Union[ReportBlock, ReportPlanBlock]) -> int:
        if isinstance(block, ReportBlock):
            return block.idx
        elif isinstance(block, ReportPlanBlock):
            return block.block.idx
        else:
            raise ValueError(f"Invalid block type: {type(block)}")

    async def aget(self, version: Optional[int] = None) -> ReportResponse:
        """Get this report's details asynchronously."""
        extra_params = []
        if version is not None:
            extra_params.append(f"version={version}")

        url = await self._build_url(f"/api/v1/reports/{self.report_id}", extra_params)

        response = await self.aclient.get(url, headers=self._headers)
        response.raise_for_status()
        return ReportResponse(**response.json())

    def get(self, version: Optional[int] = None) -> ReportResponse:
        """Synchronous wrapper for getting this report's details."""
        return self._run_sync(self.aget(version))

    async def aupdate_report(self, updated_report: Report) -> ReportResponse:
        """Update this report's content asynchronously."""
        url = await self._build_url(f"/api/v1/reports/{self.report_id}")
        response = await self.aclient.patch(
            url, headers=self._headers, json={"content": updated_report.dict()}
        )
        response.raise_for_status()
        return ReportResponse(**response.json())

    def update_report(self, updated_report: Report) -> ReportResponse:
        """Synchronous wrapper for updating this report's content."""
        return self._run_sync(self.aupdate_report(updated_report))

    async def aupdate_plan(
        self,
        action: Literal["approve", "reject", "edit"],
        updated_plan: Optional[ReportPlan] = None,
    ) -> ReportResponse:
        """Update this report's plan asynchronously."""
        if action == "edit" and not updated_plan:
            raise ValueError("updated_plan is required when action is 'edit'")

        url = await self._build_url(
            f"/api/v1/reports/{self.report_id}/plan", [f"action={action}"]
        )

        data = None
        if updated_plan is not None:
            plan_dict = updated_plan.dict()
            plan_dict.pop("generated_at", None)
            data = plan_dict

        if updated_plan is None and action == "edit":
            raise ValueError("updated_plan is required when action is 'edit'")

        response = await self.aclient.patch(url, headers=self._headers, json=data)
        response.raise_for_status()
        return ReportResponse(**response.json())

    def update_plan(
        self,
        action: Literal["approve", "reject", "edit"],
        updated_plan: Optional[ReportPlan] = None,
    ) -> ReportResponse:
        """Synchronous wrapper for updating this report's plan."""
        return self._run_sync(self.aupdate_plan(action, updated_plan))

    async def asuggest_edits(
        self,
        user_query: str,
        auto_history: bool = True,
        chat_history: Optional[List[dict]] = None,
    ) -> List[EditSuggestion]:
        """Get AI suggestions for edits to this report asynchronously.

        Args:
            user_query: The user's request/question about what to edit
            auto_history: Whether to automatically add the user's message to the chat history
            chat_history:
                A list of chat messages to include in the chat history.
                The format being a list of dictionaries with "role" and "content" keys.
        """
        # Add user message to history
        self.chat_history.append(
            Message(role=MessageRole.USER, content=user_query, timestamp=datetime.now())
        )

        # Format chat history with edit summaries
        chat_history_dicts = []
        for msg in self.chat_history[:-1]:  # Exclude current message
            content = msg.content
            if msg.role == MessageRole.USER:
                # Add edit summary for user messages
                edit_summary = self._get_edit_summary_after_message(msg.timestamp)
                if edit_summary:
                    content = f"{content}\n\nActions taken:\n{edit_summary}"

            chat_history_dicts.append({"role": msg.role.value, "content": content})

        # decide whether to include chat history or not
        if chat_history:
            chat_history_dicts = chat_history
        elif auto_history:
            chat_history_dicts = chat_history_dicts
        else:
            chat_history_dicts = []

        # Make the API call
        url = await self._build_url(f"/api/v1/reports/{self.report_id}/suggest_edits")
        data = {"user_query": user_query, "chat_history": chat_history_dicts}

        response = await self.aclient.post(url, headers=self._headers, json=data)
        response.raise_for_status()
        suggestions = response.json()
        suggestions = [EditSuggestion(**suggestion) for suggestion in suggestions]

        # Add assistant response to history
        if suggestions:
            for suggestion in suggestions:
                self.chat_history.append(
                    Message(
                        role=MessageRole.ASSISTANT,
                        content=suggestion.justification,
                        timestamp=datetime.now(),
                    )
                )

        return suggestions

    def suggest_edits(
        self,
        user_query: str,
        auto_history: bool = True,
        chat_history: Optional[List[dict]] = None,
    ) -> List[EditSuggestion]:
        """Synchronous wrapper for getting edit suggestions."""
        return self._run_sync(
            self.asuggest_edits(user_query, auto_history, chat_history)
        )

    async def await_completion(
        self, timeout: int = DEFAULT_TIMEOUT, poll_interval: int = DEFAULT_POLL_INTERVAL
    ) -> Report:
        """Wait for this report to complete processing."""
        start_time = time.time()
        while True:
            report_response = await self.aget()
            status = report_response.status

            if status == "completed":
                return report_response.report
            elif status == "error":
                events = await self.aget_events()
                raise ValueError(f"Report entered error state: {events[-1].msg}")
            elif time.time() - start_time > timeout:
                raise TimeoutError(f"Report did not complete within {timeout} seconds")

            await asyncio.sleep(poll_interval)

    def wait_for_completion(
        self, timeout: int = DEFAULT_TIMEOUT, poll_interval: int = DEFAULT_POLL_INTERVAL
    ) -> Report:
        """Synchronous wrapper for awaiting report completion."""
        return self._run_sync(self.await_completion(timeout, poll_interval))

    async def await_for_plan(
        self, timeout: int = DEFAULT_TIMEOUT, poll_interval: int = DEFAULT_POLL_INTERVAL
    ) -> ReportPlan:
        """Wait for this report's plan to be ready for review."""
        start_time = time.time()
        while True:
            report_metadata = await self.aget_metadata()
            state = report_metadata.state

            if state == "waiting_approval":
                report_response = await self.aget()
                return report_response.plan
            elif state == "error":
                events = await self.aget_events()
                raise ValueError(f"Report entered error state: {events[-1].msg}")
            elif time.time() - start_time > timeout:
                raise TimeoutError(f"Plan was not ready within {timeout} seconds")

            await asyncio.sleep(poll_interval)

    def wait_for_plan(
        self, timeout: int = DEFAULT_TIMEOUT, poll_interval: int = DEFAULT_POLL_INTERVAL
    ) -> ReportPlan:
        """Synchronous wrapper for awaiting plan readiness."""
        return self._run_sync(self.await_for_plan(timeout, poll_interval))

    async def aget_metadata(self) -> ReportMetadata:
        """Get this report's metadata asynchronously."""
        return await self._client.aget_report_metadata(self.report_id)

    def get_metadata(self) -> ReportMetadata:
        """Synchronous wrapper for getting this report's metadata."""
        return self._run_sync(self.aget_metadata())

    async def adelete(self) -> None:
        """Delete this report asynchronously."""
        return await self._client.adelete_report(self.report_id)

    def delete(self) -> None:
        """Synchronous wrapper for deleting this report."""
        return self._run_sync(self.adelete())

    async def aaccept_edit(self, suggestion: EditSuggestion) -> None:
        """Accept a suggested edit.

        Args:
            suggestion: The EditSuggestion to accept, typically from suggest_edits()
        """
        if len(suggestion.blocks) == 0:
            return

        # Determine if we're editing a plan or report based on first block type
        is_plan_edit = isinstance(suggestion.blocks[0], ReportPlanBlock)

        # Get current content
        report_response = await self.aget()
        current_blocks = (
            report_response.plan.blocks
            if is_plan_edit
            else report_response.report.blocks
        )

        # Track the edit
        new_blocks = []
        for edit_block in suggestion.blocks:
            # Find matching block in current content
            old_block = next(
                (
                    b
                    for b in current_blocks
                    if self._get_block_idx(b) == self._get_block_idx(edit_block)
                ),
                None,
            )

            old_content = (
                self._get_block_content(old_block) if old_block else "[No old content]"
            )
            new_content = self._get_block_content(edit_block)

            if is_plan_edit:
                new_queries_str = "\n".join(
                    [
                        f"Field: {q.field}, Prompt: {q.prompt}, Context: {q.context}"
                        for q in edit_block.queries
                    ]
                )
                new_dependency_str = (
                    f"Depends on: {edit_block.dependency}"
                    if edit_block.dependency
                    else ""
                )
                new_content += f"\n\n{new_queries_str}\n{new_dependency_str}"

                if old_block:
                    old_queries_str = "\n".join(
                        [
                            f"Field: {q.field}, Prompt: {q.prompt}, Context: {q.context}"
                            for q in old_block.queries
                        ]
                    )
                    old_dependency_str = (
                        f"Depends on: {old_block.dependency}"
                        if old_block.dependency
                        else ""
                    )
                    old_content += f"\n\n{old_queries_str}\n{old_dependency_str}"

            self.edit_history.append(
                EditAction(
                    block_idx=self._get_block_idx(edit_block),
                    old_content=old_content,
                    new_content=new_content,
                    action="approved",
                    timestamp=datetime.now(),
                )
            )

            # Create updated block
            if is_plan_edit:
                new_blocks.append(
                    ReportPlanBlock(
                        block=ReportBlock(
                            idx=edit_block.block.idx,
                            template=self._get_block_content(edit_block),
                            sources=edit_block.block.sources,
                        ),
                        queries=edit_block.queries,
                        dependency=edit_block.dependency,
                    )
                )
            else:
                new_blocks.append(
                    ReportBlock(
                        idx=edit_block.idx,
                        template=self._get_block_content(edit_block),
                        sources=edit_block.sources,
                    )
                )

        if new_blocks:
            if is_plan_edit:
                # Update plan in place
                plan = report_response.plan

                # Replace edited blocks and add new ones
                for new_block in new_blocks:
                    block_idx = self._get_block_idx(new_block)
                    existing_block_idx = next(
                        (
                            i
                            for i, b in enumerate(plan.blocks)
                            if b.block.idx == block_idx
                        ),
                        None,
                    )

                    if existing_block_idx is not None:
                        # Replace existing block
                        plan.blocks[existing_block_idx] = new_block
                    else:
                        # Add new block to end
                        plan.blocks.append(new_block)

                await self.aupdate_plan("edit", plan)
            else:
                # Update report in place
                report = report_response.report

                # Replace edited blocks and add new ones
                for new_block in new_blocks:
                    block_idx = self._get_block_idx(new_block)
                    existing_block_idx = next(
                        (i for i, b in enumerate(report.blocks) if b.idx == block_idx),
                        None,
                    )

                    if existing_block_idx is not None:
                        # Replace existing block
                        report.blocks[existing_block_idx] = new_block
                    else:
                        # Add new block to end
                        report.blocks.append(new_block)

                await self.aupdate_report(report)

    def accept_edit(self, suggestion: EditSuggestion) -> None:
        """Synchronous wrapper for accepting an edit."""
        return self._run_sync(self.aaccept_edit(suggestion))

    async def areject_edit(self, suggestion: EditSuggestion) -> None:
        """Reject a suggested edit.

        Args:
            suggestion: The EditSuggestion to reject, typically from suggest_edits()
        """
        # Track the rejections
        for edit_block in suggestion.blocks:
            self.edit_history.append(
                EditAction(
                    block_idx=self._get_block_idx(edit_block),
                    old_content=self._get_block_content(edit_block),
                    new_content=None,
                    action="rejected",
                    timestamp=datetime.now(),
                )
            )

    def reject_edit(self, suggestion: EditSuggestion) -> None:
        """Synchronous wrapper for rejecting an edit."""
        return self._run_sync(self.areject_edit(suggestion))

    def _get_edit_summary_after_message(
        self, message_timestamp: datetime
    ) -> Optional[str]:
        """Get a summary of edits that occurred after a specific message."""
        relevant_edits = [
            edit for edit in self.edit_history if edit.timestamp > message_timestamp
        ]

        if not relevant_edits:
            return None

        approved = [edit for edit in relevant_edits if edit.action == "approved"]
        rejected = [edit for edit in relevant_edits if edit.action == "rejected"]

        summary = []

        if approved:
            summary.append("Approved edits:")
            for edit in approved:
                summary.append(
                    f'Block {edit.block_idx}: "{edit.old_content}" -> "{edit.new_content}"'
                )

        if rejected:
            if approved:  # Add spacing if we had approved edits
                summary.append("")
            summary.append("Rejected edits:")
            for edit in rejected:
                summary.append(f'Block {edit.block_idx}: "{edit.old_content}"')

        return "\n".join(summary)

    async def aget_events(
        self, last_sequence: Optional[int] = None
    ) -> List[ReportEventItemEventData_Progress]:
        """Get all events for this report asynchronously.

        Args:
            last_sequence: If provided, only get events after this sequence number

        Returns:
            List of ReportEvent objects
        """
        extra_params = []
        if last_sequence is not None:
            extra_params.append(f"last_sequence={last_sequence}")

        url = await self._build_url(
            f"/api/v1/reports/{self.report_id}/events", extra_params
        )

        response = await self.aclient.get(url, headers=self._headers)
        response.raise_for_status()
        progress_events = []
        for event in response.json():
            if event["event_type"] == "progress":
                progress_events.append(
                    ReportEventItemEventData_Progress(**event["event_data"])
                )

        return progress_events

    def get_events(
        self, last_sequence: Optional[int] = None
    ) -> List[ReportEventItemEventData_Progress]:
        """Synchronous wrapper for getting report events."""
        return self._run_sync(self.aget_events(last_sequence))
