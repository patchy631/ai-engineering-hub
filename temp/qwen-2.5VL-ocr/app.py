#!/usr/bin/env python
# coding: utf-8

import streamlit as st
import torch
from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor
import json
import ast
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import os
from openai import OpenAI

st.set_page_config(page_title="Qwen 2.5 OCR", layout="wide")

# Sidebar for image upload
st.sidebar.title("Qwen 2.5 OCR")
uploaded_file = st.sidebar.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

# Display uploaded image in sidebar
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.sidebar.image(image, caption="Uploaded Image", use_column_width=True)
    
    # Save the uploaded image temporarily
    temp_image_path = "temp_uploaded_image.jpg"
    # Convert RGBA images to RGB before saving as JPEG
    if image.mode == 'RGBA':
        image = image.convert('RGB')
    image.save(temp_image_path)

# Helper functions
def parse_json(json_output):
    # Parsing out the markdown fencing
    lines = json_output.splitlines()
    for i, line in enumerate(lines):
        if line == "```json":
            json_output = "\n".join(lines[i+1:])  # Remove everything before "```json"
            json_output = json_output.split("```")[0]  # Remove everything after the closing "```"
            break  # Exit the loop once "```json" is found
    return json_output

def inference(image_path, prompt, sys_prompt="You are a helpful assistant.", max_new_tokens=4096, return_input=False):
    image = Image.open(image_path)
    image_local_path = "file://" + image_path
    messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"image": image_local_path},
            ]
        },
    ]
    text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    
    # image_inputs, video_inputs = process_vision_info([messages])
    inputs = processor(text=[text], images=[image], padding=True, return_tensors="pt")
    inputs = inputs.to(device)

    output_ids = model.generate(**inputs, max_new_tokens=max_new_tokens)
    generated_ids = [output_ids[len(input_ids):] for input_ids, output_ids in zip(inputs.input_ids, output_ids)]
    output_text = processor.batch_decode(generated_ids, skip_special_tokens=True, clean_up_tokenization_spaces=True)
    if return_input:
        return output_text[0], inputs
    else:
        return output_text[0]

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def inference_with_api(image_path, prompt, sys_prompt="You are a helpful assistant.", model_id="qwen2.5-vl-72b-instruct", min_pixels=512*28*28, max_pixels=2048*28*28):
    base64_image = encode_image(image_path)
    client = OpenAI(
        api_key=os.getenv('DASHSCOPE_API_KEY'),
        base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
    )

    messages=[
        {
            "role": "system",
            "content": [{"type":"text","text": sys_prompt}]},
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "min_pixels": min_pixels,
                    "max_pixels": max_pixels,
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                },
                {"type": "text", "text": prompt},
            ],
        }
    ]
    completion = client.chat.completions.create(
        model = model_id,
        messages = messages,
    )
    return completion.choices[0].message.content

def plot_text_bounding_boxes(image_path, bounding_boxes, input_width, input_height):
    """
    Plots bounding boxes on an image with markers for each a name, using PIL, normalized coordinates, and different colors.
    """
    # Load the image
    img = Image.open(image_path)
    width, height = img.size
    
    # Create a drawing object
    draw = ImageDraw.Draw(img)

    # Parsing out the markdown fencing
    bounding_boxes = parse_json(bounding_boxes)

    try:
        font = ImageFont.truetype("NotoSansCJK-Regular.ttc", size=10)
    except:
        font = ImageFont.load_default()

    # Iterate over the bounding boxes
    for i, bounding_box in enumerate(ast.literal_eval(bounding_boxes)):
        color = 'green'

        # Convert normalized coordinates to absolute coordinates
        abs_y1 = int(bounding_box["bbox_2d"][1]/input_height * height)
        abs_x1 = int(bounding_box["bbox_2d"][0]/input_width * width)
        abs_y2 = int(bounding_box["bbox_2d"][3]/input_height * height)
        abs_x2 = int(bounding_box["bbox_2d"][2]/input_width * width)

        if abs_x1 > abs_x2:
            abs_x1, abs_x2 = abs_x2, abs_x1

        if abs_y1 > abs_y2:
            abs_y1, abs_y2 = abs_y2, abs_y1

        # Draw the bounding box
        draw.rectangle(
            ((abs_x1, abs_y1), (abs_x2, abs_y2)), outline=color, width=1
        )

        # Draw the text
        if "text_content" in bounding_box:
            draw.text((abs_x1, abs_y2), bounding_box["text_content"], fill=color, font=font)

    return img

# Main content
st.title("Qwen 2.5 OCR")

# Mode selection
mode = st.radio("Select Mode", ["Full Page OCR", "Text Spotting"])

# Load model
@st.cache_resource
def load_model():
    checkpoint = "Qwen/Qwen2.5-VL-7B-Instruct"
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        checkpoint, 
        torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32,
        attn_implementation="flash_attention_2" if torch.cuda.is_available() else "eager",
        device_map="auto" if torch.cuda.is_available() else None
    )
    processor = AutoProcessor.from_pretrained(checkpoint)
    return model, processor, device

# Initialize model
with st.spinner("Loading model..."):
    model, processor, device = load_model()

if uploaded_file is not None:
    if mode == "Full Page OCR":
        st.header("Full Page OCR")
        
        if st.button("Extract Text"):
            with st.spinner("Extracting text..."):
                prompt = "Please output only the text content from the image without any additional descriptions or formatting."
                try:
                    response = inference(temp_image_path, prompt)
                    st.markdown("### Extracted Text:")
                    st.markdown(response)
                except Exception as e:
                    st.error(f"Error during inference: {str(e)}")
    
    elif mode == "Text Spotting":
        st.header("Text Spotting")
        
        if st.button("Spot Text"):
            with st.spinner("Spotting text..."):
                prompt = "Spotting all the text in the image with line-level, and output in JSON format."
                try:
                    response, inputs = inference(temp_image_path, prompt, return_input=True)
                    
                    # Get input dimensions
                    input_height = inputs['image_grid_thw'][0][1]*14
                    input_width = inputs['image_grid_thw'][0][2]*14
                    
                    # Create image with bounding boxes
                    result_image = plot_text_bounding_boxes(temp_image_path, response, input_width, input_height)
                    
                    # Display results
                    col1, col2 = st.columns(2)
                    with col1:
                        st.image(result_image, caption="Text Spotting Result", use_column_width=True)
                    with col2:
                        st.markdown("### Detected Text:")
                        st.markdown(response)
                except Exception as e:
                    st.error(f"Error during inference: {str(e)}")
else:
    st.info("Please upload an image to begin.")

# Clean up temporary file
if os.path.exists("temp_uploaded_image.jpg"):
    try:
        if not uploaded_file:
            os.remove("temp_uploaded_image.jpg")
    except:
        pass