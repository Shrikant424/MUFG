import os
from pandas import read_csv
from .vector_database import FinancialVectorDB
from typing import Dict, List


<<<<<<< Updated upstream
# Initialize vector database
vector_db = FinancialVectorDB()
db = read_csv(r"C:\mydata\MUFG\Hackathon_Dataset.csv")
=======
db = read_csv(r"D:\Manoj\Projects\Python\mufg\MUFG\Hackathon_Dataset.csv")
>>>>>>> Stashed changes
conversation_history = []

def get_relevant_context(user_message: str, user_data: Dict) -> str:
    """
    Get relevant context using FAISS vector search
    """
    try:
        # Search for relevant funds based on user message
        message_results = vector_db.search_funds(user_message, k=3, score_threshold=0.3)
        
        # Get personalized recommendations based on user profile
        profile_results = vector_db.get_fund_recommendations(user_data)
        
        # Combine results and remove duplicates
        all_results = message_results + profile_results
        seen_indices = set()
        unique_results = []
        
        for result in all_results:
            idx = result['metadata'].get('index', -1)
            if idx not in seen_indices:
                seen_indices.add(idx)
                unique_results.append(result)
                if len(unique_results) >= 5:  # Limit to top 5
                    break
        
        # Format context
        context_parts = []
        context_parts.append("=== RELEVANT FINANCIAL DATA (Vector Search Results) ===")
        
        for i, result in enumerate(unique_results, 1):
            metadata = result['metadata']
            context_parts.append(f"\n{i}. {result['document']}")
            context_parts.append(f"   Relevance Score: {result['score']:.3f}")
        
        if not unique_results:
            context_parts.append("No specific fund matches found. Using general dataset knowledge.")
        
        context_parts.append("\n=== END VECTOR SEARCH RESULTS ===\n")
        
        return "\n".join(context_parts)
        
    except Exception as e:
        print(f"Error in vector search: {e}")
        return "=== VECTOR SEARCH UNAVAILABLE ===\nUsing complete dataset for analysis.\n"

def create_enhanced_prompt(vector_context: str) -> str:
    return f"""
    You are a financial assistant specializing in retirement and superannuation planning.
    Always prioritize the RELEVANT FINANCIAL DATA from vector search results below.
    Do NOT use your own system location, and do NOT invent real-time market data or prices.
    
    {vector_context}

    Full Dataset (for reference):
    {db}    

    ### Your Responsibilities
    1. **Retirement Outlook**
    - Assess whether the user’s current contributions, savings rate, and chosen fund type are sufficient for achieving their retirement age goal.
    - Identify strengths and gaps in their plan.

    2. **Fund & Strategy Comparison**
    - Compare the user’s current fund type (e.g., growth, balanced, conservative) against at least one alternative.
    - Highlight differences in expected return, volatility, and risk profile.

    3. **Personal Profile Alignment**
    - Factor in ALL available user profile fields: country, age, gender, income, current savings, contribution rate, employment status, investment experience, risk tolerance, and retirement target age.
    - Match recommendations to both the **financial capacity** and **risk appetite** of the user.

    4. **Market & Historical Insights**
    - Incorporate historical performance patterns and general market trends for the fund, stock, ETF, or bond listed in the dataset.
    - For **stocks**, use the `Fund_Name` field to explain sector context, historical performance ranges, and common alternatives.
    - For **ETFs or bonds**, reference their typical role in a retirement portfolio and historical return patterns.
    - Do NOT provide real-time quotes, prices, or current market events.

    5. **Personalized Recommendations & Predictive Insights**
    - Suggest **actionable next steps** to improve contributions, diversify holdings, and rebalance portfolio.
    - Recommend an **allocation breakdown** (e.g., % in growth vs conservative, % in stocks vs bonds).
    - Provide both **short-term adjustments** (1–3 years) and **long-term strategies** (until retirement).
    - Use predictive reasoning based on historical trends and general market knowledge to advise on likely outcomes.

    6. **Education & Interaction**
    - Explain concepts and investment reasoning clearly to improve the user’s financial literacy.
    - Be interactive: respond naturally to follow-up questions and clarify any missing or ambiguous data.
    - Handle natural language queries from users in an intuitive manner.

    7. **Risks & Caveats**
    - Clearly outline risks such as fund fees, market volatility, inflation, and potential underperformance.
    - If any required data is missing in `{db}`, ask clarifying questions instead of guessing.

    8. **Output Style**
    - Write in a clear, structured, and easy-to-read format (use headings, bullet points, or sections).
    - Compare options side by side where relevant (pros/cons table or bulleted differences).

    9. **Disclaimer**
    Always start but only once with disclaimer only repeat when user asks for it or it feels he is more dependent on this:
    *“This is educational guidance, not professional financial advice.”*

    Format your answer with Markdown headings, bullet points, and blank lines between paragraphs.

    """
from dotenv import load_dotenv
load_dotenv()


def callLLM1(userMessage: str, userData: dict, username: str = None):
    from openai import OpenAI
    from .context_manager import ContextManager
    import getpass
    
    # Database configuration
    db_config = {
        "host": "localhost",
        "user": "root", 
        "password": "Manoj@123",
        "database": "UserData"
    }
    
    context_manager = ContextManager(db_config)

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
<<<<<<< Updated upstream
        api_key="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",
    )

    # Get relevant context using vector search
    vector_context = get_relevant_context(userMessage, userData)
    
    # Create enhanced prompt with vector context
    prompt = create_enhanced_prompt(vector_context)

=======
        api_key="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"
    )
    
>>>>>>> Stashed changes
    # Format user profile for prompt
    if userData:
        user_profile_str = "\\n".join([f"{k}: {v}" for k, v in userData.items()])
        user_profile_section = f"\\n\\nUser Profile:\\n{user_profile_str}\\n"
    else:
        user_profile_section = "\\n\\nUser Profile: (not provided)\\n"

    # Add user profile to the system prompt
    full_prompt = prompt + user_profile_section

    # Auto-get username if not provided
    if not username:
        username = getpass.getuser()
        print(f"[callLLM1] Auto-detected username: {username}")
    # Always use DB for context
    context_messages = context_manager.get_context_for_llm(username, max_messages=10)
    # Add user message to context
    result_user = context_manager.add_message(username, "user", userMessage)
    # print(f"[callLLM1] User message DB update result: {result_user}")

    # Build messages for LLM
    messages = [{"role": "system", "content": full_prompt}]
    messages.extend(context_messages)
    messages.append({"role": "user", "content": userMessage})

    response = client.chat.completions.create(
        model="deepseek/deepseek-r1-0528-qwen3-8b",
        messages=messages
    )

    assistant_reply = response.choices[0].message.content
    
    # Save assistant response to context
    result_assistant = context_manager.add_message(username, "assistant", assistant_reply)
    # print(f"[callLLM1] Assistant message DB update result: {result_assistant}")

<<<<<<< Updated upstream
    print("Response generated with vector context")
    return assistant_reply
=======
    # print("Response generated", conversation_history[-1])
    return assistant_reply


# async def callLLM1(userMessage: str, userData: dict, contextMessages: list = None):
#     """
#     Call LLM1 with proper message context
    
#     Args:
#         userMessage: Current user message
#         userData: User profile data
#         contextMessages: List of previous messages in OpenAI format [{"role": "user/assistant", "content": "..."}]
#     """
#     try:
#         client = OpenAI(
#             base_url="https://openrouter.ai/api/v1",
#             api_key="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",
#         )

#         # Format user profile for prompt
#         if userData:
#             user_profile_str = "\n".join([f"{k}: {v}" for k, v in userData.items()])
#             user_profile_section = f"\n\nUser Profile:\n{user_profile_str}\n"
#         else:
#             user_profile_section = "\n\nUser Profile: (not provided)\n"

#         # Build messages array
#         messages = [{"role": "system", "content": prompt + user_profile_section}]
        
#         # Add context messages if provided
#         if contextMessages:
#             # Limit context to prevent token overflow (last 12 messages)
#             recent_context = contextMessages[-12:] if len(contextMessages) > 12 else contextMessages
#             messages.extend(recent_context)
        
#         # Add current user message
#         messages.append({"role": "user", "content": userMessage})

#         response = client.chat.completions.create(
#             model="deepseek/deepseek-r1-0528-qwen3-8b",
#             messages=messages
#         )

#         assistant_reply = response.choices[0].message.content
#         print(f"LLM1 Response generated (context messages: {len(contextMessages) if contextMessages else 0})")
#         return assistant_reply
        
#     except Exception as e:
#         print(f"Error in callLLM1: {e}")
#         raise e

>>>>>>> Stashed changes
