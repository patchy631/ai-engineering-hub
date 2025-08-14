import os
import time
import base64
import requests
from typing import List, Dict, Any, Optional

from dotenv import load_dotenv
from groundx import GroundX, Document
from openai import OpenAI

import opik
from opik.evaluation import evaluate
from opik.evaluation.metrics import BaseMetric, GEval

load_dotenv()

def evaluate_invoice_parsing(model_output: str, expected_output: str, question: str):
    """
    Evaluate invoice parsing results using Comet Opik's GEval metrics.
    
    Args:
        model_output (str): The model's extracted answer
        expected_output (str): The expected correct answer
        question (str): The question that was asked
        
    Returns:
        dict: A dictionary containing evaluation results with the following structure:
            {
                "overall_score": float,  # Score on 0-10 scale
                "reason": str,  # Detailed reason for the score
                "passed": bool,  # Whether score >= 7.0 (70% threshold)
                "error": str, optional  # Error message if evaluation fails
            }
    """
    try:
        # Validate input
        if not model_output or not expected_output:
            raise ValueError("Model output and expected output cannot be empty")
     
        # Build the context string that includes both expected and model answers
        context = f"QUESTION: {question}\nEXPECTED_ANSWER: {expected_output}\nMODEL_ANSWER: {model_output}"

        # Define rubric scoring criteria for invoice parsing
        accuracy_rubric_text = (
            "Score 0-2: Completely incorrect or missing information\n"
            "Score 3-5: Partially correct but missing key details\n"
            "Score 6-8: Mostly correct with minor inaccuracies\n"
            "Score 9-10: Completely accurate and matches expected answer"
        )

        # Invoice Parsing Accuracy Metric
        accuracy_metric = GEval(
            task_introduction=(
                "You are an expert judge evaluating invoice parsing accuracy. "
                "Compare the model's extracted answer against the expected answer. "
                "Focus on whether the model correctly extracted the requested information. "
                "Use the following rubric to assign scores:"
            ),
            evaluation_criteria=(
                "EVALUATION STEPS:\n"
                "1. Read the QUESTION carefully to understand what information was requested.\n"
                "2. Compare the EXPECTED_ANSWER with the MODEL_ANSWER.\n"
                "3. Check if the model extracted the correct information.\n"
                "4. Consider formatting differences (e.g., '$8.45' vs '8.45' vs 'The bill total is $8.45').\n"
                "5. For 'data not available' cases, check if the model correctly indicated missing information.\n\n"
                "SCORING RUBRIC:\n"
                f"{accuracy_rubric_text}\n\n"
                "SPECIAL CASES:\n"
                "- If expected answer is 'data not available', the model should indicate information is not present\n"
                "- If expected answer has a specific value, the model should match it exactly or semantically\n"
                "- Ignore extra words like 'The bill total is' or 'The account number is' - focus on the actual value\n\n"
                "Return only a score between 0 and 10, and a concise reason that references the rubric."
            ),
            name="Invoice Parsing Accuracy",
        )

        # Run evaluation using direct GEval scoring
        accuracy_result = accuracy_metric.score(output=context)

        # Convert score from Opik's 0-1 scale to 0-10 scale
        accuracy_score = accuracy_result.value * 10

        # Return results
        return {
            "overall_score": accuracy_score,
            "reason": accuracy_result.reason,
            "passed": accuracy_score >= 7.0,  # 70% threshold
        }

    except Exception as e:
        # Error handling
        return {
            "error": f"Error evaluating invoice parsing: {str(e)}",
            "overall_score": 0.0,
            "reason": "Evaluation failed",
            "passed": False,
        }


class EvaluatorGEval:
    """Evaluator that scores answers using GEval (LLM judge with rubric)."""

    def __init__(self, groundx_api_key: str, openai_api_key: str, comet_api_key: Optional[str] = None):
        self.gx = GroundX(api_key=groundx_api_key)
        self.oa = OpenAI(api_key=openai_api_key)
        self.opik = opik.Opik(api_key=comet_api_key) if comet_api_key else opik.Opik()
        self.bucket_id = self._ensure_bucket()

    # ---------------- bucket helpers -----------------
    def _ensure_bucket(self, name: str = "gx_eval") -> str:
        for b in self.gx.buckets.list().buckets:
            if b.name == name:
                return b.bucket_id
        return self.gx.buckets.create(name=name).bucket.bucket_id

    # ---------------- ingestion helpers --------------
    def process_invoice(self, file_path: str, file_name: str, mime_type: str) -> Dict[str, Any]:
        ingest = self.gx.ingest(documents=[
            Document(
                bucket_id=int(self.bucket_id),
                file_name=file_name,
                file_path=file_path,
                file_type=mime_type.split("/")[-1],
            )
        ])
        self._poll_until_complete(ingest.ingest.process_id)
        return self._fetch_xray(file_name)

    def _poll_until_complete(self, pid: str, timeout: int = 600):
        start = time.time()
        while True:
            status = self.gx.documents.get_processing_status_by_id(process_id=pid).ingest.status
            if status in {"complete", "error", "cancelled"}:
                break
            if time.time() - start > timeout:
                raise TimeoutError("Ground X processing timed out.")
            time.sleep(3)
        if status != "complete":
            raise RuntimeError(f"Ingest finished with status {status}")

    def _fetch_xray(self, expected_name: str):
        docs = self.gx.documents.lookup(id=self.bucket_id).documents
        doc = next((d for d in docs if getattr(d, "file_name", None) == expected_name), docs[0])
        if getattr(doc, "xray_url", None):
            r = requests.get(doc.xray_url)
            r.raise_for_status()
            return r.json()
        raise RuntimeError("X-Ray URL missing")

    # ---------------- context & prompting ------------
    @staticmethod
    def _context(xray: Dict[str, Any]) -> str:
        parts = []
        if s := xray.get("fileSummary"):
            parts.append(f"Summary: {s}")
        for page in xray.get("documentPages", [])[:2]:
            texts = [ch.get("text", "")[:500] for ch in page.get("chunks", [])[:3] if ch.get("text")]
            if texts:
                parts.append("Document Content: " + " ".join(texts))
        return "\n\n".join(parts)

    def _gpt_ctx(self, q: str, ctx: str) -> str:
        prompt = (
            "You are an AI assistant analysing an invoice.\n\n" + ctx +
            f"\n\nUser Question: {q}\n\nAnswer concisely. If unknown reply 'data not available'."
        )
        resp = self.oa.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.3,
        )
        return resp.choices[0].message.content

    def _gpt_direct(self, q: str, raw: bytes, mime: str) -> str:
        img_uri = None
        if mime.startswith("image/"):
            img_uri = f"data:{mime};base64,{base64.b64encode(raw).decode()}"
            print(f"DEBUG: Using image file directly")
        elif mime == "application/pdf":
            try:
                import fitz
                page = fitz.open(stream=raw, filetype="pdf").load_page(0)
                png = page.get_pixmap(dpi=180).tobytes("png")
                img_uri = f"data:image/png;base64,{base64.b64encode(png).decode()}"
                print(f"DEBUG: Successfully converted PDF to image")
            except Exception as e:
                print(f"DEBUG: PDF conversion failed: {e}")
                # Fallback: try to extract text from PDF
                try:
                    import fitz
                    doc = fitz.open(stream=raw, filetype="pdf")
                    text = ""
                    for page in doc:
                        text += page.get_text()
                    doc.close()
                    # Send text instead of image
                    resp = self.oa.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": "You are an expert document analyser. Analyze the following invoice text and answer the question."},
                            {"role": "user", "content": f"Invoice text:\n{text}\n\nQuestion: {q}"}
                        ],
                        max_tokens=300,
                        temperature=0.3,
                    )
                    return resp.choices[0].message.content
                except Exception as e2:
                    print(f"DEBUG: Text extraction also failed: {e2}")
                    return "Error: Unable to process PDF document"
        
        user_content: List[Dict[str, Any]] = [{"type": "text", "text": f"Parse the invoice and answer: {q}"}]
        if img_uri:
            user_content.append({"type": "image_url", "image_url": {"url": img_uri}})
            print(f"DEBUG: Sending image to GPT-4o")
        else:
            print(f"DEBUG: No image available, sending text only")
        
        resp = self.oa.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "You are an expert document analyser."},
                     {"role": "user", "content": user_content}],
            max_tokens=300,
            temperature=0.3,
        )
        return resp.choices[0].message.content

    # ---------------- evaluation ---------------------
    def run(self, invoices: List[Dict[str, Any]], questions: List[str]):
        dataset = self.opik.get_or_create_dataset("GroundX vs GPT4o")
        samples = []
        for inv in invoices:
            ctx = self._context(inv["xray_data"])
            for q in questions:
                expected_output = inv.get("expected_outputs", {}).get(q, "")
                samples.append({
                    "input": f"Invoice {inv['name']} – {q}",
                    "context": ctx,
                    "invoice_name": inv["name"],
                    "expected_output": expected_output,
                })
                # Validation output for GEval parameters
                print(f"DEBUG: Question='{q}', Expected='{expected_output}' for {inv['name']}")
        
        dataset.clear(); dataset.insert(samples)

        def gx_task(sample):
            output = self._gpt_ctx(sample["input"], sample["context"])
            print(f"DEBUG: GroundX output for '{sample['input']}': '{output}'")
            return {"output": output}

        def gpt_task(sample):
            inv = next(i for i in invoices if i["name"] == sample["invoice_name"])
            output = self._gpt_direct(sample["input"], inv["raw_bytes"], inv["mime_type"])
            print(f"DEBUG: GPT-4o output for '{sample['input']}': '{output}'")
            return {"output": output}

        gx_results = []
        gpt_results = []

        for i, sample in enumerate(samples):
            model_output = gx_task(sample)["output"]
            expected_output = sample["expected_output"]
            question = sample["input"]

            gx_eval_result = evaluate_invoice_parsing(model_output, expected_output, question)
            gx_results.append(gx_eval_result)

            gpt_model_output = gpt_task(sample)["output"]
            gpt_eval_result = evaluate_invoice_parsing(gpt_model_output, expected_output, question)
            gpt_results.append(gpt_eval_result)

            # Log evaluation results to Opik dataset
            sample["groundx_score"] = gx_eval_result["overall_score"]
            sample["groundx_reason"] = gx_eval_result["reason"]
            sample["gpt4o_score"] = gpt_eval_result["overall_score"]
            sample["gpt4o_reason"] = gpt_eval_result["reason"]
            sample["groundx_output"] = model_output
            sample["gpt4o_output"] = gpt_model_output

        # Update dataset with evaluation results
        dataset.clear()
        dataset.insert(samples)

        return {"groundx_parsing": gx_results, "gpt4o_direct": gpt_results, "dataset": dataset}


def create_evaluator_geval() -> EvaluatorGEval:
    load_dotenv()
    gx_key = os.environ.get("GROUNDX_API_KEY")
    oa_key = os.environ.get("OPENAI_API_KEY")
    comet_key = os.environ.get("COMET_API_KEY")
    if not gx_key or not oa_key:
        raise ValueError("API keys missing")
    return EvaluatorGEval(gx_key, oa_key, comet_key)
