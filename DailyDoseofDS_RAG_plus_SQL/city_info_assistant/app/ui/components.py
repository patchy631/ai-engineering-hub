import streamlit as st

def init_session_state():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "workflow" not in st.session_state:
        st.session_state.workflow = None
    if "event_loop" not in st.session_state:
        st.session_state.event_loop = None

def display_available_cities():
    st.sidebar.markdown("### Available Cities")
    st.sidebar.write("You can ask questions about these cities:")
    cities = [
        "🏢 New York City",
        "🌴 Los Angeles",
        "🌆 Chicago",
        "🏭 Houston",
        "🏖️ Miami",
        "🌲 Seattle"
    ]
    for city in cities:
        st.sidebar.markdown(f"- {city}")
    
    if st.sidebar.button("Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()

def display_chat_history():
    # Display only the most recent Q&A pair
    if len(st.session_state.chat_history) >= 2:
        current_q = st.session_state.chat_history[-2]  # Most recent question
        current_a = st.session_state.chat_history[-1]  # Most recent answer
        
        st.markdown(
            f"""<div style='background-color: #f0f6ff; padding: 10px; border-radius: 5px; margin: 5px 0;'>
            {current_q}</div>""",
            unsafe_allow_html=True
        )
        st.markdown(
            f"""<div style='background-color: #f0fff0; padding: 10px; border-radius: 5px; margin: 5px 0;'>
            {current_a}</div>""",
            unsafe_allow_html=True
        )

def display_debug_info():
    with st.sidebar.expander("⚙️ Debug Information"):
        if st.session_state.workflow:
            st.write("Workflow Status: Active")
        if st.session_state.event_loop:
            st.write("Event Loop Status: Active")

def display_previous_chat():
    if len(st.session_state.chat_history) > 2:
        with st.expander("📜 Previous Chat History", expanded=False):
            # Display all except the most recent Q&A pair
            for i in range(0, len(st.session_state.chat_history) - 2, 2):
                q = st.session_state.chat_history[i]
                a = st.session_state.chat_history[i + 1]
                st.markdown(
                    f"""<div style='background-color: #f0f6ff; padding: 10px; border-radius: 5px; margin: 5px 0;'>
                    {q}</div>""",
                    unsafe_allow_html=True
                )
                st.markdown(
                    f"""<div style='background-color: #f0fff0; padding: 10px; border-radius: 5px; margin: 5px 0;'>
                    {a}</div>""",
                    unsafe_allow_html=True
                ) 