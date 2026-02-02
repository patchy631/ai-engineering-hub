#!/usr/bin/env python3
# /// script
# dependencies = [
#     "transformers>=4.36.0",
#     "peft>=0.7.0",
#     "torch>=2.0.0",
#     "accelerate>=0.24.0",
#     "huggingface_hub>=0.20.0",
#     "sentencepiece>=0.1.99",
#     "protobuf>=3.20.0",
#     "numpy",
#     "gguf",
# ]
# ///

"""
GGUF Conversion Script - Production Ready

This script converts a LoRA fine-tuned model to GGUF format for use with:
- llama.cpp
- Ollama
- LM Studio
- Other GGUF-compatible tools

Usage:
    Set environment variables:
    - ADAPTER_MODEL: Your fine-tuned model (e.g., "username/my-finetuned-model")
    - BASE_MODEL: Base model used for fine-tuning (e.g., "Qwen/Qwen2.5-0.5B")
    - OUTPUT_REPO: Where to upload GGUF files (e.g., "username/my-model-gguf")
    - HF_USERNAME: Your Hugging Face username (optional, for README)

Dependencies: All required packages are declared in PEP 723 header above.
Build tools (gcc, cmake) are installed automatically by this script.
"""

import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
from huggingface_hub import HfApi
import subprocess

print("🔄 GGUF Conversion Script")
print("=" * 60)

# Configuration from environment variables
ADAPTER_MODEL = os.environ.get("ADAPTER_MODEL", "evalstate/qwen-capybara-medium")
BASE_MODEL = os.environ.get("BASE_MODEL", "Qwen/Qwen2.5-0.5B")
OUTPUT_REPO = os.environ.get("OUTPUT_REPO", "evalstate/qwen-capybara-medium-gguf")
username = os.environ.get("HF_USERNAME", ADAPTER_MODEL.split('/')[0])

print(f"\n📦 Configuration:")
print(f"   Base model: {BASE_MODEL}")
print(f"   Adapter model: {ADAPTER_MODEL}")
print(f"   Output repo: {OUTPUT_REPO}")

# Step 1: Load base model and adapter
print("\n🔧 Step 1: Loading base model and LoRA adapter...")
print("   (This may take a few minutes)")

base_model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    dtype=torch.float16,
    device_map="auto",
    trust_remote_code=True,
)
print("   ✅ Base model loaded")

# Load and merge adapter
print("   Loading LoRA adapter...")
model = PeftModel.from_pretrained(base_model, ADAPTER_MODEL)
print("   ✅ Adapter loaded")

print("   Merging adapter with base model...")
merged_model = model.merge_and_unload()
print("   ✅ Models merged!")

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(ADAPTER_MODEL, trust_remote_code=True)
print("   ✅ Tokenizer loaded")

# Step 2: Save merged model temporarily
print("\n💾 Step 2: Saving merged model...")
merged_dir = "/tmp/merged_model"
merged_model.save_pretrained(merged_dir, safe_serialization=True)
tokenizer.save_pretrained(merged_dir)
print(f"   ✅ Merged model saved to {merged_dir}")

# Step 3: Install llama.cpp for conversion
print("\n📥 Step 3: Setting up llama.cpp for GGUF conversion...")

# CRITICAL: Install build tools FIRST (before cloning llama.cpp)
print("   Installing build tools...")
subprocess.run(
    ["apt-get", "update", "-qq"],
    check=True,
    capture_output=True
)
subprocess.run(
    ["apt-get", "install", "-y", "-qq", "build-essential", "cmake"],
    check=True,
    capture_output=True
)
print("   ✅ Build tools installed")

print("   Cloning llama.cpp repository...")
subprocess.run(
    ["git", "clone", "https://github.com/ggerganov/llama.cpp.git", "/tmp/llama.cpp"],
    check=True,
    capture_output=True
)
print("   ✅ llama.cpp cloned")

print("   Installing Python dependencies...")
subprocess.run(
    ["pip", "install", "-r", "/tmp/llama.cpp/requirements.txt"],
    check=True,
    capture_output=True
)
# sentencepiece and protobuf are needed for tokenizer conversion
subprocess.run(
    ["pip", "install", "sentencepiece", "protobuf"],
    check=True,
    capture_output=True
)
print("   ✅ Dependencies installed")

# Step 4: Convert to GGUF (FP16)
print("\n🔄 Step 4: Converting to GGUF format (FP16)...")
gguf_output_dir = "/tmp/gguf_output"
os.makedirs(gguf_output_dir, exist_ok=True)

convert_script = "/tmp/llama.cpp/convert_hf_to_gguf.py"
model_name = ADAPTER_MODEL.split('/')[-1]
gguf_file = f"{gguf_output_dir}/{model_name}-f16.gguf"

print(f"   Running: python {convert_script} {merged_dir}")
try:
    result = subprocess.run(
        [
            "python", convert_script,
            merged_dir,
            "--outfile", gguf_file,
            "--outtype", "f16"
        ],
        check=True,
        capture_output=True,
        text=True
    )
    print(result.stdout)
    if result.stderr:
        print("Warnings:", result.stderr)
except subprocess.CalledProcessError as e:
    print(f"❌ Conversion failed!")
    print("STDOUT:", e.stdout)
    print("STDERR:", e.stderr)
    raise
print(f"   ✅ FP16 GGUF created: {gguf_file}")

# Step 5: Quantize to different formats
print("\n⚙️  Step 5: Creating quantized versions...")

# Build quantize tool using CMake (more reliable than make)
print("   Building quantize tool with CMake...")
try:
    # Create build directory
    os.makedirs("/tmp/llama.cpp/build", exist_ok=True)

    # Configure with CMake
    subprocess.run(
        ["cmake", "-B", "/tmp/llama.cpp/build", "-S", "/tmp/llama.cpp",
         "-DGGML_CUDA=OFF"],  # Disable CUDA for faster build
        check=True,
        capture_output=True,
        text=True
    )

    # Build just the quantize tool
    subprocess.run(
        ["cmake", "--build", "/tmp/llama.cpp/build", "--target", "llama-quantize", "-j", "4"],
        check=True,
        capture_output=True,
        text=True
    )
    print("   ✅ Quantize tool built")
except subprocess.CalledProcessError as e:
    print(f"   ❌ Build failed!")
    print("STDOUT:", e.stdout)
    print("STDERR:", e.stderr)
    raise

# Use the CMake build output path
quantize_bin = "/tmp/llama.cpp/build/bin/llama-quantize"

# Common quantization formats
quant_formats = [
    ("Q4_K_M", "4-bit, medium quality (recommended)"),
    ("Q5_K_M", "5-bit, higher quality"),
    ("Q8_0", "8-bit, very high quality"),
]

quantized_files = []
for quant_type, description in quant_formats:
    print(f"   Creating {quant_type} quantization ({description})...")
    quant_file = f"{gguf_output_dir}/{model_name}-{quant_type.lower()}.gguf"

    subprocess.run(
        [quantize_bin, gguf_file, quant_file, quant_type],
        check=True,
        capture_output=True
    )
    quantized_files.append((quant_file, quant_type))

    # Get file size
    size_mb = os.path.getsize(quant_file) / (1024 * 1024)
    print(f"   ✅ {quant_type}: {size_mb:.1f} MB")

# Step 6: Upload to Hub
print("\n☁️  Step 6: Uploading to Hugging Face Hub...")
api = HfApi()

# Create repo
print(f"   Creating repository: {OUTPUT_REPO}")
try:
    api.create_repo(repo_id=OUTPUT_REPO, repo_type="model", exist_ok=True)
    print("   ✅ Repository created")
except Exception as e:
    print(f"   ℹ️  Repository may already exist: {e}")

# Upload FP16 version
print("   Uploading FP16 GGUF...")
api.upload_file(
    path_or_fileobj=gguf_file,
    path_in_repo=f"{model_name}-f16.gguf",
    repo_id=OUTPUT_REPO,
)
print("   ✅ FP16 uploaded")

# Upload quantized versions
for quant_file, quant_type in quantized_files:
    print(f"   Uploading {quant_type}...")
    api.upload_file(
        path_or_fileobj=quant_file,
        path_in_repo=f"{model_name}-{quant_type.lower()}.gguf",
        repo_id=OUTPUT_REPO,
    )
    print(f"   ✅ {quant_type} uploaded")

# Create README
print("\n📝 Creating README...")
readme_content = f"""---
base_model: {BASE_MODEL}
tags:
- gguf
- llama.cpp
- quantized
- trl
- sft
---

# {OUTPUT_REPO.split('/')[-1]}

This is a GGUF conversion of [{ADAPTER_MODEL}](https://huggingface.co/{ADAPTER_MODEL}), which is a LoRA fine-tuned version of [{BASE_MODEL}](https://huggingface.co/{BASE_MODEL}).

## Model Details

- **Base Model:** {BASE_MODEL}
- **Fine-tuned Model:** {ADAPTER_MODEL}
- **Training:** Supervised Fine-Tuning (SFT) with TRL
- **Format:** GGUF (for llama.cpp, Ollama, LM Studio, etc.)

## Available Quantizations

| File | Quant | Size | Description | Use Case |
|------|-------|------|-------------|----------|
| {model_name}-f16.gguf | F16 | ~1GB | Full precision | Best quality, slower |
| {model_name}-q8_0.gguf | Q8_0 | ~500MB | 8-bit | High quality |
| {model_name}-q5_k_m.gguf | Q5_K_M | ~350MB | 5-bit medium | Good quality, smaller |
| {model_name}-q4_k_m.gguf | Q4_K_M | ~300MB | 4-bit medium | Recommended - good balance |

## Usage

### With llama.cpp

```bash
# Download model
huggingface-cli download {OUTPUT_REPO} {model_name}-q4_k_m.gguf

# Run with llama.cpp
./llama-cli -m {model_name}-q4_k_m.gguf -p "Your prompt here"
```

### With Ollama

1. Create a `Modelfile`:
```
FROM ./{model_name}-q4_k_m.gguf
```

2. Create the model:
```bash
ollama create my-model -f Modelfile
ollama run my-model
```

### With LM Studio

1. Download the `.gguf` file
2. Import into LM Studio
3. Start chatting!

## License

Inherits the license from the base model: {BASE_MODEL}

## Citation

```bibtex
@misc{{{OUTPUT_REPO.split('/')[-1].replace('-', '_')},
  author = {{{username}}},
  title = {{{OUTPUT_REPO.split('/')[-1]}}},
  year = {{2025}},
  publisher = {{Hugging Face}},
  url = {{https://huggingface.co/{OUTPUT_REPO}}}
}}
```

---

*Converted to GGUF format using llama.cpp*
"""

api.upload_file(
    path_or_fileobj=readme_content.encode(),
    path_in_repo="README.md",
    repo_id=OUTPUT_REPO,
)
print("   ✅ README uploaded")

print("\n" + "=" * 60)
print("✅ GGUF Conversion Complete!")
print(f"📦 Repository: https://huggingface.co/{OUTPUT_REPO}")
print(f"\n📥 Download with:")
print(f"   huggingface-cli download {OUTPUT_REPO} {model_name}-q4_k_m.gguf")
print(f"\n🚀 Use with Ollama:")
print("   1. Download the GGUF file")
print(f"   2. Create Modelfile: FROM ./{model_name}-q4_k_m.gguf")
print("   3. ollama create my-model -f Modelfile")
print("   4. ollama run my-model")
print("=" * 60)
