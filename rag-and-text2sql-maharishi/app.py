import os, gc, uuid, asyncio, base64

import streamlit as st

from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.core import Settings

from workflow import RouterOutputAgentWorkflow
from query_tools import sql_tool, rag_tool



##### Get LLM #####

llm = Settings.llm


##### Prepare Session details #####


if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "workflow" not in st.session_state:
    st.session_state.workflow = None

if "asyncio_event_loop" not in st.session_state:
    st.session_state.asyncio_event_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(st.session_state.asyncio_event_loop)

if "id" not in st.session_state:
    st.session_state.id = uuid.uuid4()

session_id = st.session_state.id

chat_history_with_sys_msg = [ChatMessage(
                                role=MessageRole.SYSTEM,
                                content=f"""You are an helpful assistant here to provide information about US cities as per the user query.
                                        To provide information about the cities you will make use of the `sql_tool` and `city_information_tool` function and never provide any information on the US cities without calling this functions.
                                        If no information is available from the function or if the user asks any irrelevant questions not related to US cities then you politely refuse to answer.
                                        `sql_tool` will give you information about the population of US cities and `city_information_tool` will give you any information for various US cities as per the user query."""
                                       )
                            ]
def reset_chat():
    st.session_state.chat_history = []
    st.session_state.workflow = None
    st.session_state.id = uuid.uuid4()
    gc.collect()



##### async LLM call #####


async def get_llm_reply(wf, msg):
    
    result = await wf.run(message=msg)
    return str(result)


##### UI Set Up #####


st.set_page_config(page_title="Ask me about US Cities", page_icon="assets/daily_dose_of_ds_logo.jpeg", layout="wide")

with st.sidebar:
    st.markdown("""<h1 class='main-header'>👋 You can Ask Questions for the below cities:</h1>
                <h4></h4>
                <li>New York City</<li>
                <h4></h4>
                <li>Los Angeles</<li>
                <h4></h4>
                <li>Chicago</<li>
                <h4></h4>
                <li>Houston</<li>
                <h4></h4>
                <li>Miami</<li>
                <h4></h4>
                <li>Seattle</<li>
                <h4></h4>""", unsafe_allow_html=True)
    st.divider()
    st.markdown("""<h1 class='main-header'>💡 Example Question:</h1>
                <h4 class='main-header'>- Tell me about Miami</h4>
                <h4 class='main-header'>- Which city has the largest population?</h4>""", unsafe_allow_html=True)
    st.divider()
    st.markdown("""<h1 class='main-header'>🕵 Observability / Tracing:</h1>
                <h4 class='main-header'>If using local deployment of Opik then:</h4><a href='http://localhost:5173/'>Click Here</a>""", unsafe_allow_html=True)
    st.divider()

col1, col2, col3 = st.columns([1, 5, 1])

with col1:
    pass

with col2:
    st.markdown("<h1 class='main-header'>Ask me about US Cities 🇺🇸</h1>", unsafe_allow_html=True)
    st.divider()
    st.markdown("<h5 class='main-header'>🛠️ Implemented Using:</h5>", unsafe_allow_html=True)
    st.image(['assets/logos.png'], width=600)
    
with col3:
    st.button("🔄 Start a New Chat", on_click=reset_chat)



##### Chat Set Up #####


# Initialize chat history
if "chat_history" not in st.session_state:
    with col2:
      reset_chat()

# Display chat messages from history on app rerun
for message in st.session_state.chat_history:
    with col2:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


if not st.session_state.workflow:
        wf = RouterOutputAgentWorkflow(llm=llm, tools=[sql_tool, rag_tool],
                                       chat_history = chat_history_with_sys_msg,
                                       verbose=True, timeout=60.0*20)
        st.session_state.workflow = wf

# Accept user input
if prompt := st.chat_input("Ask about US Cities..."):
    # Add user message to chat history
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with col2:
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            try:                
                with st.spinner("please wait.."):
                    full_response = st.session_state.asyncio_event_loop.run_until_complete(get_llm_reply(st.session_state.workflow, prompt))
                    message_placeholder.markdown(full_response)
            except Exception as e:
                print('error: ',e)
                full_response = 'Sorry...encountered some error.'

        # Add assistant response to chat history
        st.session_state.chat_history.append({"role": "assistant", "content": full_response})
