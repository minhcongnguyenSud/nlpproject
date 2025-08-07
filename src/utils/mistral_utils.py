"""
Shared Mistral AI utilities for Newsletter Generator

Th                print(f"Mistral AI test successful: {result}")
                return True
        else:
        print("Mistral AI test failed: No valid response")
        return False
        
    except Exception as e:
        print(f"Mistral AI test failed: {e}")e provides common Mistral AI client functionality to avoid code duplication.
"""

from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

from ..core import config


def create_mistral_client():
    """
    Create and return a configured Mistral AI client.
    
    Returns:
        MistralClient: Configured Mistral client
        
    Raises:
        ValueError: If API key is invalid
        Exception: If client creation fails
    """
    try:
        # Validate API key
        if not config.MISTRAL_API_KEY or len(config.MISTRAL_API_KEY) < 10:
            raise ValueError("Invalid Mistral API key. Please check your .env file.")
        
        client = MistralClient(api_key=config.MISTRAL_API_KEY)
        print("Connected to Mistral AI")
        return client
        
    except Exception as e:
        print(f"Error creating Mistral client: {e}")
        raise


def test_mistral_connection():
    """
    Test the connection to Mistral AI with a simple request.
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        client = create_mistral_client()
        
        # Test with a simple request
        messages = [ChatMessage(role="user", content="Say 'Hello' in one word.")]
        
        response = client.chat(
            model="mistral-small-latest",
            messages=messages,
            max_tokens=10,
            temperature=0.1,
        )
        
        if response and response.choices and len(response.choices) > 0:
            result = response.choices[0].message.content.strip()
            if result:
                print(f"Mistral AI test successful: {result}")
                return True
        
        print("Mistral AI test failed: No valid response")
        return False
        
    except Exception as e:
        print(f"Mistral AI test failed: {e}")
        return False
