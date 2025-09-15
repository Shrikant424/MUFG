from openai import OpenAI
import requests

prompt = """
You are a stock symbol extraction specialist. Your ONLY job is to identify stock symbols from user messages.

Rules:
1. Extract valid stock ticker symbols (2-5 uppercase letters like AAPL, GOOGL, TSLA)
2. Convert company names to their stock symbols (e.g., "Apple" -> "AAPL", "Tesla" -> "TSLA")
3. If multiple symbols are found, return the FIRST one
4. If NO stock symbols are found, return exactly "NONE"
5. Return ONLY the stock symbol, nothing else

Common mappings:
- Apple -> AAPL
- Google/Alphabet -> GOOGL  
- Microsoft -> MSFT
- Tesla -> TSLA
- Amazon -> AMZN
- Meta/Facebook -> META
- NVIDIA -> NVDA
- Netflix -> NFLX

Examples:
User: "What's Apple's stock price?"
You: AAPL

User: "I want to invest in Tesla"
You: TSLA

User: "How is my retirement plan?"
You: NONE

User: "Show me GOOGLE analysis"
You: GOOGL
"""

def callLLM3(userMessage: str = None, llm2_response: str = None, userData: dict = None, conversation_history: list = None):
    """
    Extract stock symbols from either user message or LLM2 response and trigger model predictions
    
    Args:
        userMessage: Original user message (optional)
        llm2_response: Response from LLM2 to analyze for stock symbols
        userData: User profile data
        conversation_history: Previous conversation context
    
    Returns:
        dict: Contains stock symbol and prediction data if found
    """
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key="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"
    )

    # Determine which text to analyze - prioritize LLM2 response
    text_to_analyze = llm2_response if llm2_response else userMessage
    
    if not text_to_analyze:
        return {"stock_symbol": "", "prediction_data": None, "error": "No text provided for analysis"}

    # Profile (optional)
    if userData:
        user_profile_str = "\n".join([f"{k}: {v}" for k, v in userData.items()])
        user_profile_section = f"\n\nUser Profile:\n{user_profile_str}\n"
    else:
        user_profile_section = "\n\nUser Profile: (not provided)\n"

    # Base system instruction
    messages = [
        {"role": "system", "content": prompt + user_profile_section}
    ]

    # Add past conversation if available
    if conversation_history:
        recent_history = conversation_history[-1:]
        messages.extend(recent_history)

    # Add the text to analyze (either user message or LLM2 response)
    messages.append({"role": "user", "content": text_to_analyze})

    try:
        # Call LLM to extract stock symbol
        response = client.chat.completions.create(
            model="deepseek/deepseek-r1-0528-qwen3-8b",
            messages=messages
        )

        assistant_reply = response.choices[0].message.content.strip()

        # 🔑 If model says NONE → return empty result
        if assistant_reply.upper() == "NONE":
            return {"stock_symbol": "", "prediction_data": None}

        # Update conversation history
        if conversation_history is not None:
            conversation_history.append({"role": "user", "content": text_to_analyze})
            conversation_history.append({"role": "assistant", "content": assistant_reply})

        # If we found a stock symbol, get predictions
        stock_symbol = assistant_reply.upper()
        prediction_data = None
        
        try:
            # Call the prediction model
            prediction_response = requests.post(
                "http://localhost:8000/predict-stock",
                json={"symbol": stock_symbol, "years": 2},
                headers={"Content-Type": "application/json"},
                timeout=30  # 30 second timeout
            )
            
            if prediction_response.status_code == 200:
                prediction_data = prediction_response.json()
            else:
                print(f"Prediction API error: {prediction_response.status_code}")
                
        except Exception as e:
            print(f"Error calling prediction API: {e}")

        return {
            "stock_symbol": stock_symbol,
            "prediction_data": prediction_data,
            "source": "llm2_response" if llm2_response else "user_message"
        }

    except Exception as e:
        print(f"Error in callLLM3: {e}")
        return {"stock_symbol": "", "prediction_data": None, "error": str(e)}
