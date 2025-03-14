import streamlit as st
import os
import time
import asyncio

c1,c2 = st.columns([1.5,10])
with c2:
    st.title("Patient Case Summarizer")
with c1:
    st.image("https://cdn-icons-png.flaticon.com/512/428/428373.png",use_container_width=True)
st.divider()

if "openai_key" not in st.session_state:
    st.session_state.openai_key = ''
if "llama_key" not in st.session_state:
    st.session_state.llama_key = ''


if st.session_state.openai_key == '' or st.session_state.llama_key == '':
    openai_placeholder = st.empty()  # Create a placeholder for the name input
    llama_placeholder = st.empty()
    button_placeholder = st.empty()
    success_message = st.empty()

    with openai_placeholder:
        openai_input = st.text_input('Enter OPEN AI key')
    with llama_placeholder:
        llama_input = st.text_input('Enter LLAMA CLOUD API key')

    with button_placeholder:
        submit_button = st.button('Submit')

    if openai_placeholder and llama_placeholder and submit_button:
        os.environ['OPENAI_API_KEY'] = openai_input
        st.session_state.openai_key = openai_input
        os.environ['LLAMA_CLOUD_API_KEY'] = llama_input
        st.session_state.llama_key = llama_input
        openai_placeholder.empty()
        llama_placeholder.empty()
        with success_message:
            st.success("Keys initialised in environment")
        time.sleep(2)
        success_message.empty()
        button_placeholder.empty()

@st.cache_resource
def get_workflow():
        from src.agent import workflow, LogEvent
        return workflow, LogEvent

if st.session_state.llama_key and st.session_state.openai_key:
    
    workflow, LogEvent = get_workflow()
    chat_input = st.chat_input("enter message here")
    st.chat_message(chat_input, avatar='user')
    if chat_input:
        handler = workflow.run(patient_json_path="data/almeta_buckridge.json")

        response_dict = asyncio.run(handler)
        st.chat_message(str(response_dict["case_summary"]), avatar='assistant')