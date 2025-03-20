import streamlit as st
import torch
import numpy as np
from transformers import AutoConfig, AutoModelForCausalLM
from janus.models import MultiModalityCausalLM, VLChatProcessor
from PIL import Image

# -----------------------------
#  1. Load Model and Processor
# -----------------------------
@st.cache_resource
def load_model_and_processor(model_path="deepseek-ai/Janus-1.3B"):
    config = AutoConfig.from_pretrained(model_path)
    language_config = config.language_config
    # Force eager attention implementation (sometimes needed depending on environment)
    language_config._attn_implementation = 'eager'
    
    vl_gpt_model = AutoModelForCausalLM.from_pretrained(
        model_path,
        language_config=language_config,
        trust_remote_code=True
    )
    vl_gpt_model = vl_gpt_model.to(torch.bfloat16 if torch.cuda.is_available() else torch.float16)
    if torch.cuda.is_available():
        vl_gpt_model = vl_gpt_model.cuda()

    vl_chat_proc = VLChatProcessor.from_pretrained(model_path)
    return vl_gpt_model, vl_chat_proc

vl_gpt, vl_chat_processor = load_model_and_processor()
tokenizer = vl_chat_processor.tokenizer
cuda_device = 'cuda' if torch.cuda.is_available() else 'cpu'


# -------------------------------------
#  2. Multimodal Understanding Section
# -------------------------------------
@torch.inference_mode()
def multimodal_understanding(image, question, seed, top_p, temperature):
    # Clear CUDA cache before generating
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    # Set seed
    torch.manual_seed(seed)
    np.random.seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)

    # Build conversation
    conversation = [
        {
            "role": "User",
            "content": f"<image_placeholder>\n{question}",
            "images": [image],
        },
        {"role": "Assistant", "content": ""},
    ]

    # Prepare inputs
    pil_image = Image.open(image).convert("RGB")
    prepared_inputs = vl_chat_processor(
        conversations=conversation, images=[pil_image], force_batchify=True
    ).to(cuda_device, dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float16)

    # Prepare input embeddings
    inputs_embeds = vl_gpt.prepare_inputs_embeds(**prepared_inputs)

    # Generate output
    outputs = vl_gpt.language_model.generate(
        inputs_embeds=inputs_embeds,
        attention_mask=prepared_inputs.attention_mask,
        pad_token_id=tokenizer.eos_token_id,
        bos_token_id=tokenizer.bos_token_id,
        eos_token_id=tokenizer.eos_token_id,
        max_new_tokens=512,
        do_sample=(temperature > 0),
        temperature=temperature,
        top_p=top_p
    )

    answer = tokenizer.decode(outputs[0].cpu().tolist(), skip_special_tokens=True)
    return answer


# ----------------------------------
#  3. Image Generation Support Code
# ----------------------------------
@torch.inference_mode()
def generate(
    input_ids,
    width,
    height,
    temperature=1.0,
    parallel_size=5,
    cfg_weight=5.0,
    image_token_num_per_image=576,
    patch_size=16
):
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    
    # Expand input tokens for conditional & unconditional branches
    tokens = torch.zeros((parallel_size * 2, len(input_ids)), dtype=torch.int).to(cuda_device)
    for i in range(parallel_size * 2):
        tokens[i, :] = input_ids
        if i % 2 != 0:
            tokens[i, 1:-1] = vl_chat_processor.pad_id

    # Convert tokens to embeddings
    inputs_embeds = vl_gpt.language_model.get_input_embeddings()(tokens)
    generated_tokens = torch.zeros((parallel_size, image_token_num_per_image), dtype=torch.int).to(cuda_device)

    pkv = None
    for i in range(image_token_num_per_image):
        outputs = vl_gpt.language_model.model(
            inputs_embeds=inputs_embeds,
            use_cache=True,
            past_key_values=pkv
        )
        pkv = outputs.past_key_values
        hidden_states = outputs.last_hidden_state
        logits = vl_gpt.gen_head(hidden_states[:, -1, :])
        logit_cond = logits[0::2, :]
        logit_uncond = logits[1::2, :]
        # Classifier-Free Guidance
        logits = logit_uncond + cfg_weight * (logit_cond - logit_uncond)
        probs = torch.softmax(logits / temperature, dim=-1)
        next_token = torch.multinomial(probs, num_samples=1)
        generated_tokens[:, i] = next_token.squeeze(dim=-1)
        next_token = torch.cat([next_token.unsqueeze(dim=1), next_token.unsqueeze(dim=1)], dim=1).view(-1)
        # Prepare the next image embeddings
        img_embeds = vl_gpt.prepare_gen_img_embeds(next_token)
        inputs_embeds = img_embeds.unsqueeze(dim=1)

    # Decode the image tokens
    patches = vl_gpt.gen_vision_model.decode_code(
        generated_tokens.to(dtype=torch.int),
        shape=[parallel_size, 8, width // patch_size, height // patch_size]
    )

    return generated_tokens.to(dtype=torch.int), patches

def unpack(decoded_patches, width, height, parallel_size=5):
    decoded_patches = decoded_patches.to(torch.float32).cpu().numpy().transpose(0, 2, 3, 1)
    decoded_patches = np.clip((decoded_patches + 1) / 2 * 255, 0, 255)

    visual_img = np.zeros((parallel_size, width, height, 3), dtype=np.uint8)
    visual_img[:, :, :] = decoded_patches
    return visual_img

@torch.inference_mode()
def generate_image(prompt, seed=None, guidance=5):
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    # Set the seed for reproducible results
    if seed is not None:
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed(seed)
        np.random.seed(seed)

    width = 384
    height = 384
    parallel_size = 5

    # Prepare input text (the model expects a conversation format)
    messages = [{'role': 'User', 'content': prompt},
                {'role': 'Assistant', 'content': ''}]
    text = vl_chat_processor.apply_sft_template_for_multi_turn_prompts(
        conversations=messages,
        sft_format=vl_chat_processor.sft_format,
        system_prompt=''
    )
    text += vl_chat_processor.image_start_tag

    input_ids = torch.LongTensor(tokenizer.encode(text))
    output, patches = generate(
        input_ids,
        width // 16 * 16,
        height // 16 * 16,
        cfg_weight=guidance,
        parallel_size=parallel_size
    )

    images = unpack(patches, width // 16 * 16, height // 16 * 16)
    pil_images = [
        Image.fromarray(images[i]).resize((1024, 1024), Image.LANCZOS)
        for i in range(parallel_size)
    ]
    return pil_images


# ---------------------------
#  4. Build Streamlit Layout
# ---------------------------
def main():
    st.title("Janus - Streamlit Demo")

    # Create two tabs: one for Multimodal Understanding, one for Text-to-Image
    tab1, tab2 = st.tabs(["Multimodal Understanding", "Text-to-Image Generation"])

    # Sidebar for image upload and parameters
    with st.sidebar:
        st.header("Upload Image")
        uploaded_image = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
        
        st.header("Parameters")
        
        # Multimodal Understanding Parameters
        with st.expander("Multimodal Understanding Settings", expanded=True):
            seed = st.number_input("Seed", min_value=0, value=42, step=1)
            top_p = st.slider("top_p", min_value=0.0, max_value=1.0, value=0.95, step=0.05)
            temperature = st.slider("temperature", min_value=0.0, max_value=1.0, value=0.1, step=0.05)
        
        # Text-to-Image Parameters
        with st.expander("Text-to-Image Settings", expanded=True):
            seed_t2i = st.number_input("Seed (Optional)", min_value=0, value=12345, step=1)
            cfg_weight = st.slider("CFG Weight", min_value=1.0, max_value=10.0, value=5.0, step=0.5)

    # Main content area
    with tab1:
        st.subheader("Ask a question about your image")
        if uploaded_image:
            st.image(uploaded_image, use_column_width=True)
        question = st.text_input("Question", value="Explain this meme...")

        if st.button("Chat"):
            if not uploaded_image:
                st.warning("Please upload an image before chatting.")
            else:
                with st.spinner('Analyzing your image...'):
                    answer = multimodal_understanding(
                        image=uploaded_image,
                        question=question,
                        seed=seed,
                        top_p=top_p,
                        temperature=temperature
                    )
                st.text_area("Response", value=answer, height=150)

    with tab2:
        st.subheader("Generate Images From Text")
        prompt = st.text_area("Prompt", value="A cute baby fox in autumn leaves, digital art, cinematic lighting...")

        if st.button("Generate Images"):
            with st.spinner('Generating images... This may take a minute.'):
                images = generate_image(prompt=prompt, seed=seed_t2i, guidance=cfg_weight)
            st.write("Generated Images:")
            cols = st.columns(2)
            idx = 0
            for i in range(2):  # 2 rows
                for j in range(2):  # 2 cols
                    if idx < len(images):
                        with cols[j]:
                            st.image(images[idx], use_column_width=True)
                    idx += 1

        # Tips / example prompts
        with st.expander("Example Prompts"):
            st.write("1. A cyberpunk samurai meditating in a neon-lit Japanese garden, cherry blossoms falling.")
            st.write("2. A magical library with floating books, ethereal lighting, dust particles in the air, hyperrealistic detail.")
            st.write("3. A steampunk-inspired coffee machine with brass gears and copper pipes, Victorian era style, morning light.")


if __name__ == "__main__":
    main()