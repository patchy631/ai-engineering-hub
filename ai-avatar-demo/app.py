import streamlit as st
import streamlit.components.v1 as components
import asyncio

# Your services
from services.zep_service import zep_service
from services.anam_service import anam_service
from config.settings import settings

# -------------------------------
# STREAMLIT UI CONFIG
# -------------------------------

st.set_page_config(
    page_title="Zep AI Assistant",
    layout="wide"
)

st.title("AI Consultant")
st.caption("Powered by Zep Knowledge Graph + Anam AI Avatar")

st.markdown("""
    <div style="padding: 1rem 0; display: flex; gap: 2rem; align-items: center;">
        <img src="https://www.getzep.com/cdn-cgi/image/width=256,format=auto/zep-logo-lockup-daisy-bush-rgb.svg" width="150" style="margin-bottom: 1rem;" onerror="this.style.display='none'">
        <img src="https://anam.ai/favicon.ico" width="50" style="margin-bottom: 1rem;" onerror="this.style.display='none'">
    </div>""", unsafe_allow_html=True)

# Custom CSS for cleaner UI
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    .stButton button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)


# -------------------------------
# Session Setup (Zep)
# -------------------------------

if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "anam_session_token" not in st.session_state:
    st.session_state.anam_session_token = None

# Sidebar for session management
with st.sidebar:
    st.header("Session Management")

    # User name input
    user_name = st.text_input(
        "Your Name", value="Demo User", key="user_name_input")

    if st.button("Initialize New Session", type="primary"):
        # Generate user_id from name
        user_id = user_name.lower().replace(" ", "-")
        session_id = f"session-{user_id}"

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            # Create Zep user
            loop.run_until_complete(
                zep_service.create_user(
                    user_id=user_id,
                    first_name=user_name.split()[0] if user_name else "Demo"
                )
            )

            # Create Zep thread
            loop.run_until_complete(
                zep_service.create_thread(
                    thread_id=session_id,
                    user_id=user_id
                )
            )

            # Clear old session data
            st.session_state.user_id = user_id
            st.session_state.session_id = session_id
            st.session_state.anam_session_token = None

            st.success(f"Session initialized for {user_name}!")
            st.rerun()

        except Exception as e:
            st.error(f"Error initializing session: {e}")

    # Display current session info
    if st.session_state.session_id:
        st.divider()
        st.info(f"**Active User:** {st.session_state.user_id}")
        st.caption(f"Session: {st.session_state.session_id}")

        if st.button("Restart Anam Session", type="secondary"):
            st.session_state.anam_session_token = None
            st.success("Anam session ended!")
            st.rerun()

        st.caption("End the session when done to save costs")


# -------------------------------
# MAIN: ANAM AVATAR INTERFACE
# -------------------------------

if st.session_state.session_id:
    if st.session_state.anam_session_token is None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        session_data = loop.run_until_complete(
            anam_service.create_session_token(
                persona_name="Zep Assistant",
                system_prompt="You are a helpful AI assistant with access to relevant knowledge to assist the user.",
                avatar_id=settings.anam_avatar_id,
                voice_id=settings.anam_voice_id,
                llm_id="CUSTOMER_CLIENT_V1"  # Explicitly set custom LLM mode
            )
        )

        if not session_data or "sessionToken" not in session_data:
            st.error("Failed to create Anam session token.")
            st.stop()

        st.session_state.anam_session_token = session_data["sessionToken"]
        st.success("Anam session created with custom LLM!")

    session_token = st.session_state.anam_session_token

    # Center the avatar

    # Full HTML block for Anam avatar
    # NOTE: Calls FastAPI backend at http://localhost:8000
    anam_html = f"""
<!DOCTYPE html>
<html>
<head>
  <style>
    body {{
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 20px;
    }}
    #persona-video {{
      width: 100%;
      max-width: 600px;
      border-radius: 12px;
      background:black;
      margin: 0 auto;
    }}
    #status {{
      text-align:center;
      margin-top:10px;
      font-size:12px;
      color:#666;
      font-weight: 500;
    }}
    .controls {{
      text-align: center;
      margin-top: 15px;
    }}
    button {{
      padding: 8px 20px;
      margin: 0 5px;
      border-radius: 6px;
      border: none;
      cursor: pointer;
      font-size: 14px;
    }}
    .start-btn {{
      background: #4CAF50;
      color: white;
    }}
    .stop-btn {{
      background: #f44336;
      color: white;
    }}
    .end-btn {{
      background: #ff9800;
      color: white;
    }}
  </style>
</head>
<body>

  <video id="persona-video" autoplay playsinline></video>
  <div id="status">Initializing…</div>
  <div class="controls">
    <button class="start-btn" id="start-btn" onclick="startConversation()">Start Conversation</button>
    <button class="stop-btn" id="stop-btn" onclick="stopConversation()" style="display:none;">Stop Conversation</button>
    <button class="end-btn" id="end-btn" onclick="endSession()">End Session</button>
  </div>

  <script type="module">
    import {{ createClient }} from "https://esm.sh/@anam-ai/js-sdk@latest";
    import {{ AnamEvent }} from "https://esm.sh/@anam-ai/js-sdk@latest/dist/module/types";

    const sessionToken = "{session_token}";
    const sessionId    = "{st.session_state.session_id}";
    const statusEl     = document.getElementById("status");
    const startBtn     = document.getElementById("start-btn");
    const stopBtn      = document.getElementById("stop-btn");
    const endBtn       = document.getElementById("end-btn");
    
    let anamClient = null;

    // ---- Custom LLM Response Handler ----
    async function handleUserMessage(messageHistory) {{
      console.log('Message history updated:', messageHistory);
      
      // Only respond to user messages
      if (messageHistory.length === 0) {{
        console.log('Empty message history, skipping');
        return;
      }}
      
      const lastMessage = messageHistory[messageHistory.length - 1];
      if (lastMessage.role !== 'user') {{
        console.log('Last message not from user, skipping');
        return;
      }}

      if (!anamClient) {{
        console.error('Anam client not initialized');
        return;
      }}

      try {{
        console.log('Getting custom LLM response with Zep KG');
        console.log('User message:', lastMessage.content);
        
        // Convert Anam message format to standard format
        const messages = messageHistory.map((msg) => ({{
          role: msg.role === 'user' ? 'user' : 'assistant',
          content: msg.content,
        }}));

        console.log('Sending request to backend:', `http://localhost:8000/llm/stream?session_id=${{sessionId}}`);

        // Create a streaming talk session FIRST
        const talkStream = anamClient.createTalkMessageStream();
        console.log('Talk stream created, active:', talkStream.isActive());
        
        // Give the stream a moment to initialize
        await new Promise(resolve => setTimeout(resolve, 50));

        // Call our FastAPI backend with Zep integration
        const response = await fetch(
          `http://localhost:8000/llm/stream?session_id=${{sessionId}}`,
          {{
            method: "POST",
            headers: {{ "Content-Type": "application/json" }},
            body: JSON.stringify({{ messages }}),
          }}
        );

        console.log('Response received, status:', response.status);
        console.log('Response headers:', Array.from(response.headers.entries()));

        if (!response.ok) {{
          const errorText = await response.text();
          console.error('Backend error response:', errorText);
          throw new Error(`Backend returned ${{response.status}}: ${{errorText}}`);
        }}
        
        // Verify we got the right content type
        const contentType = response.headers.get('content-type');
        console.log('Content-Type:', contentType);
        if (!contentType || !contentType.includes('text/event-stream')) {{
          console.warn('Expected text/event-stream but got:', contentType);
        }}

        const reader = response.body?.getReader();
        if (!reader) {{
          throw new Error('Failed to get response stream reader');
        }}

        const textDecoder = new TextDecoder();
        console.log('Starting to stream LLM response to Anam persona...');
        
        let chunkCount = 0;
        let totalContent = '';

        // Stream the response chunks to the persona
        while (true) {{
          const {{ done, value }} = await reader.read();

          if (done) {{
            console.log('LLM streaming complete');
            console.log(`Received ${{chunkCount}} chunks, total length: ${{totalContent.length}}`);
            if (talkStream.isActive()) {{
              console.log('Ending talk stream');
              talkStream.endMessage();
            }}
            break;
          }}

          if (value) {{
            const text = textDecoder.decode(value, {{ stream: true }});
            const lines = text.split('\\n').filter((line) => line.trim());

            for (const line of lines) {{
              if (line.startsWith('data: ')) {{
                try {{
                  const jsonStr = line.slice(6);
                  const data = JSON.parse(jsonStr);
                  
                  if (data.content) {{
                    chunkCount++;
                    totalContent += data.content;
                    
                    if (talkStream.isActive()) {{
                      talkStream.streamMessageChunk(data.content, false);
                      if (chunkCount % 10 === 0) {{
                        console.log(`Streamed ${{chunkCount}} chunks so far...`);
                      }}
                    }} else {{
                      console.warn('Talk stream no longer active at chunk', chunkCount);
                      break;
                    }}
                  }}
                }} catch (parseError) {{
                  console.warn('Failed to parse SSE data:', line, parseError);
                }}
              }}
            }}
          }}
        }}
        
        console.log('Final response:', totalContent.substring(0, 100) + '...');
        
      }} catch (error) {{
        console.error('Custom LLM error:', error);
        console.error('Error details:', {{
          message: error.message,
          stack: error.stack,
          name: error.name
        }});
        
        // Check if it's a network error (backend not running)
        if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {{
          console.error('BACKEND NOT REACHABLE - Is FastAPI running on port 8000?');
          if (anamClient) {{
            anamClient.talk(
              "I cannot connect to the backend server. Please ensure the FastAPI server is running on port 8000."
            );
          }}
        }} else if (anamClient) {{
          anamClient.talk(
            "I'm sorry, I encountered an error while processing your request. Please check the console for details."
          );
        }}
      }}
    }}

    // ---- Startup ----
    async function start() {{
      try {{
        statusEl.textContent = "Connecting…";
        
        // Test backend connectivity
        console.log('Testing backend connection...');
        try {{
          const healthCheck = await fetch('http://localhost:8000/health');
          if (healthCheck.ok) {{
            console.log('Backend is reachable');
          }} else {{
            console.warn('Backend health check failed:', healthCheck.status);
          }}
        }} catch (e) {{
          console.error('Backend is NOT reachable. Make sure FastAPI is running on port 8000');
          console.error('Run: uvicorn backend:app --reload');
        }}

        // Create Anam client
        anamClient = createClient(sessionToken);

        // Set up event listeners
        anamClient.addListener(AnamEvent.SESSION_READY, () => {{
          console.log('Anam session ready - Custom LLM with Zep KG active!');
          statusEl.textContent = "Connected - Custom LLM active";
          statusEl.style.color = "#22c55e";
          startBtn.style.display = "inline-block";
          stopBtn.style.display = "none";
          endBtn.style.display = "inline-block";
        }});

        anamClient.addListener(AnamEvent.CONNECTION_CLOSED, () => {{
          console.log('🔌 Connection closed');
          statusEl.textContent = "Disconnected";
          statusEl.style.color = "#dc3545";
        }});

        // This is the KEY event for custom LLM integration
        anamClient.addListener(AnamEvent.MESSAGE_HISTORY_UPDATED, handleUserMessage);

        // Handle stream interruptions
        anamClient.addListener(AnamEvent.TALK_STREAM_INTERRUPTED, () => {{
          console.log('Talk stream interrupted by user');
        }});

        // Start streaming to video element
        await anamClient.streamToVideoElement("persona-video");

        console.log('Custom LLM persona with Zep KG started successfully!');
      }} catch (error) {{
        console.error('Failed to start conversation:', error);
        statusEl.textContent = `Error: ${{error.message}}`;
        statusEl.style.color = "#dc3545";
      }}
    }}
    
    // Button handlers
    window.startConversation = function() {{
      if (anamClient) {{
        anamClient.talk("Hello! How can I help you today?");
        startBtn.style.display = "none";
        stopBtn.style.display = "inline-block";
        statusEl.textContent = "Listening...";
      }}
    }};
    
    window.stopConversation = function() {{
      if (anamClient) {{
        anamClient.stopStreaming();
        startBtn.style.display = "inline-block";
        stopBtn.style.display = "none";
        statusEl.textContent = "Connected - Custom LLM active";
      }}
    }};
    
    window.endSession = function() {{
      if (anamClient) {{
        anamClient.stopStreaming();
        statusEl.textContent = "Session ended.";
        statusEl.style.color = "#ff9800";
        startBtn.style.display = "none";
        stopBtn.style.display = "none";
        endBtn.style.display = "none";
      }}
    }};

    start();
  </script>
</body>
</html>
    """

    # Render the avatar
    components.html(anam_html, height=650, scrolling=False)

else:
    st.info("Please initialize a session from the sidebar to start.")
