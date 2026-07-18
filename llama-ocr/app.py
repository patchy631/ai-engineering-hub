import streamlit as st
import ollama
from PIL import Image
import io
import fitz  # PyMuPDF
import re  # Regular expressions for string cleaning

# Page configuration
st.set_page_config(
    page_title="Llama OCR",
    page_icon="🦙",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title and description in main area
st.title("🦙 Llama OCR")

# Add clear button to top right
col1, col2 = st.columns([6, 1])
with col2:
    if st.button("Clear 🗑️"):
        if 'ocr_result' in st.session_state:
            del st.session_state['ocr_result']
        st.rerun()

st.markdown('<p style="margin-top: -20px;">Extract structured text from images using Llama 3.2 Vision!</p>', unsafe_allow_html=True)
st.markdown("---")

# Function to clean and extract numeric amount from a string
def extract_amount(amount_string):
    # Remove any non-numeric characters (e.g., '$', 'Total Amount:', spaces, etc.)
    cleaned_string = re.sub(r'[^\d.,]', '', amount_string)  # Keep digits, commas, and periods

    # Replace commas with dots for decimal conversion (e.g., '155,00' -> '155.00')
    cleaned_string = cleaned_string.replace(',', '.')

    # Ensure there are no multiple dots, keeping only the last one as the decimal separator
    if cleaned_string.count('.') > 1:
        cleaned_string = cleaned_string.rsplit('.', 1)[0] + '.' + cleaned_string.rsplit('.', 1)[1]
    
    # Remove thousands separators (commas) and convert to float
    cleaned_string = cleaned_string.replace(',', '')

    try:
        # Convert to float and format to two decimal places
        return round(float(cleaned_string), 2)
    except ValueError:
        return None  # Return None if we can't convert to float

# Function to convert PDF to image using in-memory byte stream
def pdf_to_image(pdf_file):
    pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")  # Open PDF directly from byte stream
    # Convert the first page to an image
    page = pdf_document[0]  # Get the first page
    pix = page.get_pixmap()
    img_data = pix.tobytes("png")  # Convert to PNG image bytes
    img = Image.open(io.BytesIO(img_data))  # Open the image from bytes
    return img

# Input field for the user to enter an amount
st.sidebar.header("Enter Amount")
user_amount = st.sidebar.number_input("Amount", min_value=0.0, format="%.2f")

# Move upload controls to sidebar
with st.sidebar:
    st.header("Upload Image")
    uploaded_file = st.file_uploader("Choose an image...", type=['png', 'jpg', 'jpeg', 'pdf'])

    if uploaded_file is not None:
        if uploaded_file.type == 'application/pdf':
            # If the uploaded file is a PDF, convert it to an image
            with st.spinner("Converting PDF to image..."):
                try:
                    image = pdf_to_image(uploaded_file)
                    st.image(image, caption="Converted Image from PDF")
                except Exception as e:
                    st.error(f"Error converting PDF: {str(e)}")
        else:
            # If it's an image file, load it directly
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image")

        # Convert the image to bytes (PNG/JPG format) before sending to OCR
        image_bytes = io.BytesIO()
        image.save(image_bytes, format='PNG')  # Convert to PNG format
        image_bytes.seek(0)  # Reset the stream pointer to the beginning

        if st.button("Extract Text 🔍", type="primary"):
            with st.spinner("Processing image..."):
                try:
                    # Send the image as bytes to Ollama OCR model
                    response = ollama.chat(
                        model='llama3.2-vision',
                        messages=[{
                            'role': 'user',
                            'content': """Give me the total amount only.""",
                            'images': [image_bytes.getvalue()]
                        }]
                    )
                    extracted_amount = response.message.content
                    st.session_state['ocr_result'] = extracted_amount

                    # Clean the extracted amount and convert it to float
                    cleaned_amount = extract_amount(extracted_amount)

                    if cleaned_amount is not None:
                        # Compare the amount entered by the user with the amount from the file
                        if round(user_amount, 2) == cleaned_amount:
                            st.success(f"✅ The entered amount matches the extracted amount: {cleaned_amount:.2f}")
                        else:
                            st.warning(f"❌ The entered amount ({user_amount:.2f}) does not match the extracted amount: {cleaned_amount:.2f}")
                    else:
                        st.error(f"Error: Unable to extract a valid amount from the OCR result: {extracted_amount}")
                except Exception as e:
                    st.error(f"Error processing image: {str(e)}")

# Main content area for results
if 'ocr_result' in st.session_state:
    st.markdown(f"**Extracted Amount:** {st.session_state['ocr_result']}")
else:
    st.info("Upload an image and click 'Extract Text' to see the results here.")

# Footer
st.markdown("---")
st.markdown("Made with ❤️ using Llama Vision Model2 | [Report an Issue](https://github.com/patchy631/ai-engineering-hub/issues)")
