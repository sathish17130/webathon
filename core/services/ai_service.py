"""
AI Service Module
Handles AI-generated explanations for recommendations.
"""

import requests

# Placeholder API key - Replace with .env key later
API_KEY = "XXXX"

# OpenAI API endpoint
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"


def get_ai_explanation(prompt_text):
    """
    Get AI-generated explanation from OpenAI API.
    
    Args:
        prompt_text: The prompt/question to send to AI
    
    Returns:
        Explanation text string, or error message if API call fails
    """
    # If API key is placeholder, return a mock explanation
    if API_KEY == "XXXX":
        return (
            "This is a placeholder AI explanation. To enable real AI explanations:\n"
            "1. Create a .env file in the project root\n"
            "2. Add: OPENAI_API_KEY=your_actual_api_key\n"
            "3. Update this file to use: import os; from dotenv import load_dotenv; load_dotenv(); API_KEY = os.getenv('OPENAI_API_KEY')\n\n"
            "For now, here's a sample explanation:\n\n"
            "Based on your preferences, this item scored highest because it offers the best balance "
            "between price, rating, performance, and battery life according to your specified weights. "
            "It represents excellent value for your budget and aligns well with your priorities."
        )
    
    # Prepare headers
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Prepare payload
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant that explains product recommendations clearly and concisely."
            },
            {
                "role": "user",
                "content": prompt_text
            }
        ],
        "max_tokens": 200,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(OPENAI_API_URL, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        explanation = data.get('choices', [{}])[0].get('message', {}).get('content', 'No explanation available.')
        
        return explanation
    
    except requests.exceptions.RequestException as e:
        return f"Error fetching AI explanation: {str(e)}. Please check your API key and internet connection."


def generate_explanation(best_item, category):
    """
    Generate an explanation for the best_item in a dynamic spec-based comparison.

    Args:
        best_item: UserItem instance (expects .item_name and .specifications)
        category: Category instance

    Returns:
        Explanation text (placeholder if API key is not set).
    """
    specs = best_item.specifications or {}
    top_specs_preview = ", ".join([f"{k}={v}" for k, v in list(specs.items())[:8]])

    prompt = (
        f"We compared multiple user-entered options in category '{category.name}'.\n"
        f"The best option is '{best_item.item_name}'.\n"
        f"Specifications (partial): {top_specs_preview}\n\n"
        "Explain in simple, e-commerce style why this option is the best based on the weighted numeric specs.\n"
        "Keep it concise and beginner-friendly."
    )
    return get_ai_explanation(prompt)
