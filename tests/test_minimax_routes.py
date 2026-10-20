"""Offline request tests: python -m unittest discover -s tests -v.

Requires the projects' openai, httpx, litellm, requests, python-dotenv and
pydantic-settings dependencies. All inference HTTP transports are mocked.
"""
import ast
import asyncio
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import httpx
import requests


ROOT = Path(__file__).resolve().parents[1]
COMPARISON = ROOT / "minimaxm2-vs-sonnet4-5-vs-kimik2-vs-gemini3"
FLASH = "minimax/minimax-m3.1-flash:free"
MODELS = (FLASH, "minimax/minimax-m3", "minimax/minimax-m2", "custom/model")
ENV = {
    "OPENROUTER_API_KEY": "test-key",
    "ANAM_API_KEY": "test-key",
    "ZEP_API_KEY": "test-key",
    "ZEP_DOCS_USER_ID": "offline-user",
    "LITELLM_LOCAL_MODEL_COST_MAP": "True",
}


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def completion_response(request, streaming):
    if streaming:
        chunk = {
            "id": "offline-completion",
            "object": "chat.completion.chunk",
            "created": 0,
            "model": FLASH,
            "choices": [{"index": 0, "delta": {"content": "answer"}, "finish_reason": None}],
        }
        return httpx.Response(
            200, request=request,
            headers={"Content-Type": "text/event-stream"},
            content=f"data: {json.dumps(chunk)}\n\ndata: [DONE]\n\n".encode(),
        )
    return httpx.Response(200, request=request, json={
        "id": "offline-completion",
        "object": "chat.completion",
        "created": 0,
        "model": FLASH,
        "choices": [{"index": 0, "message": {"role": "assistant", "content": "answer"}, "finish_reason": "stop"}],
    })


class MiniMaxRoutesTest(unittest.TestCase):
    def setUp(self):
        self.environment = patch.dict(os.environ, ENV, clear=True)
        self.environment.start()
        self.addCleanup(self.environment.stop)
        # Never load a developer's .env file in an offline transport test.
        self.dotenv = patch("dotenv.load_dotenv", return_value=False)
        self.dotenv.start()
        self.addCleanup(self.dotenv.stop)
        self.network = patch("socket.socket.connect", side_effect=AssertionError("Network access is disabled in offline tests"))
        self.network.start()
        self.addCleanup(self.network.stop)

    def assert_request(self, request, model):
        self.assertEqual(str(request.url), "https://openrouter.ai/api/v1/chat/completions")
        self.assertEqual(request.method, "POST")
        body = json.loads(request.content)
        self.assertEqual(body["model"], model)
        for field in ("service_tier", "thinking", "reasoning_effort", "reasoning_split"):
            self.assertNotIn(field, body)
        return body

    def test_avatar_stream_and_fallback_preserve_model_and_history(self):
        config = load_module("avatar_settings", ROOT / "ai-avatar-demo/config/settings.py")
        history = [
            {"role": "user", "content": [
                {"type": "text", "text": "Describe this."},
                {"type": "image_url", "image_url": {"url": "https://example.invalid/image.png"}},
            ]},
            {"role": "assistant", "content": None,
             "reasoning_details": [{"type": "reasoning.text", "text": "retained reasoning"}],
             "tool_calls": [{"id": "call_1", "type": "function", "function": {"name": "lookup", "arguments": "{}"}}]},
            {"role": "tool", "tool_call_id": "call_1", "content": "retained tool result"},
        ]
        original = json.loads(json.dumps(history))
        for model in MODELS:
            for fallback in (False, True):
                with self.subTest(model=model, fallback=fallback):
                    if model == FLASH:
                        os.environ.pop("OPENROUTER_MODEL", None)
                    else:
                        os.environ["OPENROUTER_MODEL"] = model
                    settings = config.Settings(_env_file=None)
                    self.assertEqual(settings.openrouter_model, model)
                    original_config = sys.modules.get("config")
                    sys.modules["config"] = SimpleNamespace(settings=settings)
                    try:
                        service = load_module("avatar_llm", ROOT / "ai-avatar-demo/services/llm_service.py")
                    finally:
                        if original_config is None:
                            sys.modules.pop("config", None)
                        else:
                            sys.modules["config"] = original_config
                    captured = []

                    async def send(client, request, **kwargs):
                        body = self.assert_request(request, model)
                        captured.append(body)
                        self.assertEqual(body["messages"], [{"role": "system", "content": "system"}] + original)
                        self.assertEqual(body["temperature"], 0.8)
                        self.assertEqual(body["max_tokens"], 2048)
                        if fallback and body["stream"]:
                            return httpx.Response(400, request=request, json={"error": {"message": "offline stream failure"}})
                        return completion_response(request, body["stream"])

                    async def run():
                        try:
                            with patch.object(httpx.AsyncClient, "send", send):
                                return [part async for part in service.llm_service.stream_chat_completion(history, "system")]
                        finally:
                            await service.llm_service.client.close()

                    with contextlib.redirect_stdout(io.StringIO()):
                        self.assertEqual(asyncio.run(run()), ["answer"])
                    self.assertEqual([body["stream"] for body in captured], [True, False] if fallback else [True])
                    self.assertEqual(history, original)

    def test_podcast_serialized_request_preserves_explicit_model(self):
        module = load_module("podcast_script", ROOT / "ai-podcast-generator/script_generator.py")
        for model in MODELS:
            with self.subTest(model=model):
                if model == FLASH:
                    os.environ.pop("OPENROUTER_MODEL", None)
                else:
                    os.environ["OPENROUTER_MODEL"] = model
                captured = []

                def send(session, request, **kwargs):
                    self.assertEqual(request.url, "https://openrouter.ai/api/v1/chat/completions")
                    self.assertEqual(request.method, "POST")
                    body = json.loads(request.body)
                    captured.append(body)
                    self.assertEqual(body["model"], model)
                    self.assertEqual(set(body), {"model", "messages"})
                    self.assertIn("article content", body["messages"][0]["content"])
                    response = requests.Response()
                    response.status_code = 200
                    response._content = b'{"choices":[{"message":{"content":"podcast script"}}]}'
                    return response

                with patch.object(requests.Session, "send", send):
                    self.assertEqual(module.ScriptGenerator().generate("article content"), "podcast script")
                self.assertEqual(len(captured), 1)

    def test_notebook_uses_real_sdk_with_default_and_explicit_models(self):
        from openai import OpenAI
        notebook = json.loads((ROOT / "ai-avatar-demo/zep_demo.ipynb").read_text())
        cell = next(cell for cell in notebook["cells"] if "def ask_with_knowledge(" in "".join(cell["source"]))
        source = "".join(cell["source"])
        zep = SimpleNamespace(graph=SimpleNamespace(search=lambda **kwargs: SimpleNamespace(
            episodes=[SimpleNamespace(content="retrieved context")]
        )))
        for model in MODELS:
            with self.subTest(model=model):
                if model == FLASH:
                    os.environ.pop("OPENROUTER_MODEL", None)
                else:
                    os.environ["OPENROUTER_MODEL"] = model
                captured = []

                def send(client, request, **kwargs):
                    body = self.assert_request(request, model)
                    captured.append(body)
                    self.assertIn("retrieved context", body["messages"][1]["content"])
                    self.assertIn("question", body["messages"][1]["content"])
                    return completion_response(request, False)

                with OpenAI(api_key="test-key", base_url="https://openrouter.ai/api/v1") as client:
                    namespace = {"os": os, "zep": zep, "DEMO_USER_ID": "offline-user", "openrouter_client": client}
                    exec(compile(source, "zep_demo.ipynb", "exec"), namespace)
                    with patch.object(httpx.Client, "send", send), contextlib.redirect_stdout(io.StringIO()):
                        self.assertEqual(namespace["ask_with_knowledge"]("question"), "answer")
                self.assertEqual(len(captured), 1)

    def test_comparison_choices_and_legacy_transport(self):
        module = load_module("comparison_models", COMPARISON / "model_service.py")
        names = module.get_all_model_names()
        self.assertEqual([name for name in names if name.startswith("MiniMax")], ["MiniMax M3.1 Flash", "MiniMax M3"])
        self.assertNotIn("Minimax M2", names)
        self.assertIn("Minimax M2", module.get_all_model_names("Minimax M2"))
        self.assertEqual(module.get_all_model_names("Minimax M2", "Minimax M2").count("Minimax M2"), 1)
        self.assertFalse(module.validate_model_name("unknown"))
        for name, model in (("MiniMax M3.1 Flash", FLASH), ("MiniMax M3", "minimax/minimax-m3"), ("Minimax M2", "minimax/minimax-m2")):
            with self.subTest(model=model):
                captured = []

                async def send(client, request, **kwargs):
                    body = self.assert_request(request, model)
                    captured.append(body)
                    self.assertTrue(body["stream"])
                    self.assertEqual(body["max_tokens"], 2000)
                    self.assertIn("repository context", body["messages"][0]["content"])
                    return completion_response(request, True)

                async def run():
                    with patch.object(httpx.AsyncClient, "send", send):
                        return [part async for part in module.get_model_response_async(name, "write code", {"content": "repository context"})]

                self.assertEqual(asyncio.run(run()), ["answer"])
                self.assertEqual(len(captured), 1)

    def test_picker_keeps_saved_model_and_results(self):
        module = load_module("picker_models", COMPARISON / "model_service.py")
        # Execute the application's actual selection block without starting its UI or services.
        tree = ast.parse((COMPARISON / "app.py").read_text())
        start = next(index for index, node in enumerate(tree.body) if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "all_models" for target in node.targets))
        end = next(index for index, node in enumerate(tree.body) if isinstance(node, ast.With) and any(isinstance(item.context_expr, ast.Attribute) and item.context_expr.attr == "sidebar" for item in node.items))
        selection = compile(ast.Module(body=tree.body[start:end], type_ignores=[]), "app.py", "exec")
        for saved in (None, "Minimax M2"):
            with self.subTest(saved=saved):
                state = SimpleNamespace(
                    selected_models={"model1": "Claude Sonnet 4.5" if saved else None, "model2": saved},
                    last_generated_code={"model1": "saved code", "model2": "saved code"},
                    evaluation_results={"model1": "saved result", "model2": "saved result"},
                )
                options_seen = []

                def selectbox(label, options, index, key):
                    options_seen.append(options)
                    return options[index]

                st = SimpleNamespace(session_state=state, selectbox=selectbox)
                exec(selection, {"st": st, "get_all_model_names": module.get_all_model_names,
                                 "col1": contextlib.nullcontext(), "col2": contextlib.nullcontext()})
                self.assertEqual(state.selected_models["model2"], saved or "MiniMax M3.1 Flash")
                self.assertEqual(state.last_generated_code["model2"], "saved code")
                self.assertEqual(state.evaluation_results["model2"], "saved result")
                self.assertEqual("Minimax M2" in options_seen[0], saved is not None)


if __name__ == "__main__":
    unittest.main()
