from config import openai_client, OPENAI_MODEL
from tools import vector_search_tool, calculator_tool
from memory import store_chat_message, retrieve_session_history

def tool_selector(user_input, session_history=None):
    messages = [
        {
            "role": "system",
            "content": (
                "Select the appropriate tool from the options below. Consider the full context of the conversation before deciding.\n\n"
                "Tools available:\n"
                "- vector_search_tool: Retrieve specific context from the MongoDB earnings report document. Use this for questions about MongoDB, its products, programs, acquisitions, financials, or any topics that might be covered in the document\n"
                "- calculator_tool: For mathematical operations\n"
                "- none: Only for general questions that are clearly unrelated to the document content\n\n"

                "Process for making your decision:\n"
                "1. When in doubt, prefer vector_search_tool - it can answer questions about MongoDB, its programs (like MAAP), products, acquisitions, financials, and announcements\n"
                "2. Analyze if the current question relates to or follows up on a previous vector search query\n"
                "3. For follow-up questions, incorporate context from previous exchanges to create a comprehensive search query\n"
                "4. Only use calculator_tool for explicit mathematical operations\n"
                "5. Default to none only when certain the question is completely unrelated to the document\n\n"
                
                "When continuing a conversation:\n"
                "- Identify the specific topic being discussed\n"
                "- Include relevant details from previous exchanges\n"
                "- Formulate a query that stands alone but preserves conversation context\n\n"
                
                "Return a JSON object only: {\"tool\": \"selected_tool\", \"input\": \"your_query\"}"
           )
        }
    ]
    if session_history:
        messages.extend(session_history)
    messages.append({"role": "user", "content": user_input})
    
    response = openai_client.chat.completions.create(
      model=OPENAI_MODEL,
      messages=messages
    ).choices[0].message.content
    try:
        tool_call = eval(response)
        return tool_call.get("tool"), tool_call.get("input")
    except:
        return "none", user_input

def generate_response(session_id: str, user_input: str) -> str:
    
    store_chat_message(session_id, "user", user_input)

    llm_input = []

    session_history = retrieve_session_history(session_id)
    llm_input.extend(session_history)

    user_message = {
        "role": "user",
        "content": user_input
    }
    llm_input.append(user_message)

    tool, tool_input = tool_selector(user_input, session_history)
    print("Tool selected: ", tool)
    
    if tool == "vector_search_tool":
        context = vector_search_tool(tool_input)
        system_message_content = (
            f"Answer the user's question based on the retrieved context and conversation history.\n"
            f"1. First, understand what specific information the user is requesting\n" 
            f"2. Then, locate the most relevant details in the context provided\n"
            f"3. Finally, provide a clear, accurate response that directly addresses the question\n\n"
            f"If the current question builds on previous exchanges, maintain continuity in your answer.\n"
            f"Only state facts clearly supported by the provided context. If information is not available, say 'I DON'T KNOW'.\n\n"
            f"Context:\n{context}"
        )
        response = get_llm_response(llm_input, system_message_content)
    elif tool == "calculator_tool":
        response = calculator_tool(tool_input)
    else:
        system_message_content = "You are a helpful assistant. Respond to the user's prompt as best as you can based on the conversation history."
        response = get_llm_response(llm_input, system_message_content)
    
    store_chat_message(session_id, "system", response)
    return response

def get_llm_response(messages, system_message_content):
    system_message = {
        "role": "system",
        "content": system_message_content,
    }
    
    if any(msg.get("role") == "system" for msg in messages):
        messages.append(system_message)
    else:
        messages = [system_message] + messages
    
    response = openai_client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages
    ).choices[0].message.content
    
    return response
