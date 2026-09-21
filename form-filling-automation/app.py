"""Streamlit UI for Generic Form Automation Agent."""

import base64
from datetime import datetime
import json
import os
import tempfile

from crewai import Crew, Process
from crewai.events import (
    AgentExecutionCompletedEvent,
    AgentExecutionErrorEvent,
    AgentExecutionStartedEvent,
    BaseEventListener,
    CrewKickoffCompletedEvent,
    CrewKickoffStartedEvent,
)
import streamlit as st

from flow import (
    create_document_scanner_agent,
    create_fill_form_task,
    create_form_filler_agent,
    create_form_transformer_agent,
    create_scan_document_task,
    create_transform_data_task,
)
from models import FormSchema, GenericFormData, list_available_schemas, load_schema


# ── CrewAI Event Listener ─────────────────────────────────────────────────
class StreamlitLogListener(BaseEventListener):
    """Captures CrewAI events into a list for Streamlit display."""

    def __init__(self):
        self.logs: list[dict] = []
        super().__init__()

    def setup_listeners(self, crewai_event_bus):
        @crewai_event_bus.on(CrewKickoffStartedEvent)
        def on_crew_started(source, event):
            self.logs.append(
                {
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "type": "crew",
                    "icon": "rocket",
                    "message": f"Crew '{event.crew_name}' started",
                }
            )

        @crewai_event_bus.on(CrewKickoffCompletedEvent)
        def on_crew_completed(source, event):
            self.logs.append(
                {
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "type": "crew",
                    "icon": "check",
                    "message": f"Crew '{event.crew_name}' completed",
                    "detail": str(event.output) if event.output else None,
                }
            )

        @crewai_event_bus.on(AgentExecutionStartedEvent)
        def on_agent_started(source, event):
            self.logs.append(
                {
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "type": "agent",
                    "icon": "brain",
                    "message": f"Agent '{event.agent.role}' started working",
                }
            )

        @crewai_event_bus.on(AgentExecutionCompletedEvent)
        def on_agent_completed(source, event):
            self.logs.append(
                {
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "type": "agent",
                    "icon": "white_check_mark",
                    "message": f"Agent '{event.agent.role}' completed",
                    "detail": str(event.output) if event.output else None,
                }
            )

        @crewai_event_bus.on(AgentExecutionErrorEvent)
        def on_agent_error(source, event):
            self.logs.append(
                {
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "type": "error",
                    "icon": "x",
                    "message": f"Agent error: {event.error}",
                }
            )

    def clear(self):
        self.logs.clear()

    def render(self):
        """Render collected logs as formatted text for st.code / st.markdown."""
        lines = []
        for entry in self.logs:
            ts = entry["time"]
            msg = entry["message"]
            lines.append(f"[{ts}] {msg}")
            if entry.get("detail"):
                for dl in entry["detail"].splitlines():
                    lines.append(f"         {dl}")
        return "\n".join(lines) if lines else "(no events captured)"

    def display(self):
        """Render logs inside a scrollable container in Streamlit."""
        text = self.render()
        st.html(
            f'<pre style="max-height:400px; overflow-y:auto; '
            f"background:#0e1117; color:#fafafa; padding:1em; "
            f"border-radius:0.5em; font-size:13px; "
            f'white-space:pre-wrap; word-wrap:break-word;">'
            f"{text}</pre>"
        )


st.set_page_config(
    page_title="Form Automation Agent",
    page_icon=":page_facing_up:",
    layout="wide",
)

# ── Header ──────────────────────────────────────────────────────────────────
st.markdown("# :page_facing_up: Form Automation Agent")
powered_by_html = """
    <div style='display: flex; align-items: center; gap: 10px; margin-top: -10px;'>
        <span style='font-size: 20px; color: #666;'>Powered by</span>
        <img src="https://github.com/sitammeur/test-assets/blob/main/datalab-logo.png?raw=true" width="50">
        <span style='font-size: 20px; color: #666;'>and</span>
        <img src="https://github.com/crewAIInc/crewAI/raw/main/docs/images/crewai_logo.png" width="120">
    </div>
"""
st.markdown(powered_by_html, unsafe_allow_html=True)
st.divider()


# ── Helpers ─────────────────────────────────────────────────────────────────
def pdf_preview(pdf_bytes: bytes, height: int = 400):
    """Render an inline PDF preview using a base64 iframe."""
    b64 = base64.b64encode(pdf_bytes).decode()
    st.markdown(
        f'<iframe src="data:application/pdf;base64,{b64}" '
        f'width="100%" height="{height}px" style="border:none;"></iframe>',
        unsafe_allow_html=True,
    )


def extract_json_from_text(text: str) -> dict:
    """Extract JSON from text that may contain markdown code blocks."""
    import re

    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to find JSON in markdown code block
    json_pattern = r"```(?:json)?\s*([\s\S]*?)```"
    matches = re.findall(json_pattern, text)
    for match in matches:
        try:
            return json.loads(match.strip())
        except json.JSONDecodeError:
            continue

    # Try to find raw JSON object
    brace_pattern = r"\{[\s\S]*\}"
    matches = re.findall(brace_pattern, text)
    for match in matches:
        try:
            return json.loads(match)
        except json.JSONDecodeError:
            continue

    return {}


# ── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### :gear: Form Schema")

    # Load available schemas
    available_schemas = list_available_schemas("schemas")

    if available_schemas:
        schema_options = {s["form_name"]: s["path"] for s in available_schemas}
        selected_schema_name = st.selectbox(
            "Select Form Type",
            options=list(schema_options.keys()),
            help="Choose the type of form to fill",
        )
        selected_schema_path = schema_options[selected_schema_name]

        # Show schema details
        try:
            schema = load_schema(selected_schema_path)
            with st.expander("Schema Details", expanded=False):
                st.write(f"**Form Type:** {schema.form_type}")
                st.write(f"**Fields:** {len(schema.fields)}")
                st.write("**Field Names:**")
                for f in schema.fields:
                    req = "required" if f.required else "optional"
                    st.write(f"- `{f.name}` ({req})")
        except Exception as e:
            st.error(f"Error loading schema: {e}")
            schema = None
    else:
        st.warning("No schemas found in 'schemas/' directory")
        schema = None
        selected_schema_path = None

    # Allow custom schema upload
    st.markdown("---")
    custom_schema_file = st.file_uploader(
        "Or upload custom schema (YAML)",
        type=["yaml", "yml"],
        key="custom_schema",
        help="Upload a custom form schema file",
    )
    if custom_schema_file:
        try:
            import yaml

            schema_data = yaml.safe_load(custom_schema_file.getvalue().decode("utf-8"))
            schema = FormSchema.from_dict(schema_data)
            st.success(f"Loaded custom schema: {schema.form_name}")
        except Exception as e:
            st.error(f"Invalid schema file: {e}")
            schema = None

    st.markdown("---")
    st.markdown("### :arrow_up: Documents")

    identity_file = st.file_uploader(
        "Source document (PDF)",
        type=["pdf"],
        key="identity",
        help="Upload your source document (e.g. identity document, data source).",
    )
    if identity_file:
        pdf_preview(identity_file.getvalue(), height=250)

    st.markdown("---")
    st.markdown("### :clipboard: Blank Form")

    blank_form_file = st.file_uploader(
        "Upload blank form (PDF)",
        type=["pdf"],
        key="blank_form",
        help="Upload blank form PDF to be filled.",
    )
    if blank_form_file:
        pdf_preview(blank_form_file.getvalue(), height=250)

    st.markdown("---")
    run_disabled = identity_file is None or blank_form_file is None or schema is None
    run_clicked = st.button(
        ":rocket: Run Agent",
        disabled=run_disabled,
        type="primary",
        use_container_width=True,
        help="Kicks off multi-agent workflow: Scan -> Transform -> Fill.",
    )

# ── Idle state ──────────────────────────────────────────────────────────────
if not run_clicked:
    if schema is None:
        st.warning("Please select or upload a form schema to continue.")
    else:
        st.info(
            f"Ready to fill **{schema.form_name}**. "
            "Upload your source document and blank form in sidebar, "
            "then click **Run Agent** to start."
        )
    st.stop()

# ── Workflow execution ──────────────────────────────────────────────────────
tmp_dir = tempfile.mkdtemp(prefix="form_agent_")

identity_path = os.path.join(tmp_dir, identity_file.name)
with open(identity_path, "wb") as f:
    f.write(identity_file.getvalue())

blank_form_path = os.path.join(tmp_dir, blank_form_file.name)
with open(blank_form_path, "wb") as f:
    f.write(blank_form_file.getvalue())

output_filename = f"{schema.form_type}_completed.pdf"
output_path = os.path.join(tmp_dir, output_filename)

# Create the event listener once — it auto-registers with the CrewAI event bus
log_listener = StreamlitLogListener()

steps_container = st.container()
extracted_text: str = ""
form_data: GenericFormData | None = None
failed = False

# ── Step 1: Scan document ───────────────────────────────────────────────────
with steps_container:
    with st.status(
        ":mag: **Step 1/3** — Scanning source document...", expanded=True
    ) as s1:
        try:
            log_listener.clear()

            scanner_agent = create_document_scanner_agent()
            scan_task = create_scan_document_task(scanner_agent)

            crew = Crew(
                agents=[scanner_agent],
                tasks=[scan_task],
                process=Process.sequential,
                verbose=True,
            )
            result = crew.kickoff(inputs={"document_file": identity_path})

            extracted_text = result.raw if result.raw else ""
            if not extracted_text:
                raise ValueError("No text extracted from document")
            if extracted_text.startswith("Error:"):
                raise ValueError(extracted_text)

            log_listener.display()
            s1.update(
                label=":white_check_mark: **Step 1/3** — Document scanned",
                state="complete",
                expanded=False,
            )
        except Exception as exc:
            log_listener.display()
            s1.update(
                label=":x: **Step 1/3** — Scan failed",
                state="error",
                expanded=True,
            )
            st.error(f"Document scan error: {exc}")
            failed = True

# ── Step 2: Transform data ──────────────────────────────────────────────────
if not failed:
    with steps_container:
        with st.status(
            f":arrows_counterclockwise: **Step 2/3** — Transforming data for {schema.form_name}...",
            expanded=True,
        ) as s2:
            try:
                log_listener.clear()

                transformer_agent = create_form_transformer_agent(schema)
                transform_task = create_transform_data_task(transformer_agent, schema)

                crew = Crew(
                    agents=[transformer_agent],
                    tasks=[transform_task],
                    process=Process.sequential,
                    verbose=True,
                )
                result = crew.kickoff(inputs={"extracted_text": extracted_text})

                # Parse result into GenericFormData (handles bool -> string conversion)
                raw_output = result.raw if result.raw else "{}"
                parsed = extract_json_from_text(raw_output)
                form_data = GenericFormData.from_dict(parsed)

                log_listener.display()
                s2.update(
                    label=":white_check_mark: **Step 2/3** — Data transformed",
                    state="complete",
                    expanded=False,
                )
            except Exception as exc:
                log_listener.display()
                s2.update(
                    label=":x: **Step 2/3** — Transform failed",
                    state="error",
                    expanded=True,
                )
                st.error(f"Data transform error: {exc}")
                failed = True

# ── Step 3: Fill form ───────────────────────────────────────────────────────
if not failed:
    with steps_container:
        with st.status(
            f":pencil2: **Step 3/3** — Filling {schema.form_name} PDF...", expanded=True
        ) as s3:
            try:
                log_listener.clear()

                filler_agent = create_form_filler_agent(schema)
                fill_task = create_fill_form_task(filler_agent, schema)

                crew = Crew(
                    agents=[filler_agent],
                    tasks=[fill_task],
                    process=Process.sequential,
                    verbose=True,
                )
                crew.kickoff(
                    inputs={
                        "form_data": json.dumps(form_data.to_tool_format(), indent=2),
                        "blank_form_path": blank_form_path,
                        "output_path": output_path,
                    }
                )

                log_listener.display()
                s3.update(
                    label=":white_check_mark: **Step 3/3** — Form filled",
                    state="complete",
                    expanded=False,
                )
            except Exception as exc:
                log_listener.display()
                s3.update(
                    label=":x: **Step 3/3** — Fill failed",
                    state="error",
                    expanded=True,
                )
                st.error(f"Form fill error: {exc}")
                failed = True

if failed:
    st.stop()

# ── Results ─────────────────────────────────────────────────────────────────
st.balloons()
st.divider()

col_data, col_result = st.columns([3, 2], gap="large")

with col_data:
    st.markdown(f"### :bar_chart: Extracted Data for {schema.form_name}")
    if form_data:
        st.json(form_data.to_tool_format())
    else:
        st.info("No extracted data available.")

with col_result:
    st.markdown("### :white_check_mark: Completed Form")
    if os.path.exists(output_path):
        with open(output_path, "rb") as f:
            pdf_bytes = f.read()
        st.success(f"{schema.form_name} filled successfully!")
        pdf_preview(pdf_bytes)
        st.download_button(
            label=":arrow_down: Download Completed PDF",
            data=pdf_bytes,
            file_name=output_filename,
            mime="application/pdf",
            use_container_width=True,
        )
    else:
        st.warning("Completed PDF not found at expected output path.")
