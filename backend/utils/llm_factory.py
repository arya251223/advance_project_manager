import os
from langchain_ollama import OllamaLLM
from backend.config import settings

# Force set LiteLLM environment variables
os.environ['LITELLM_REQUEST_TIMEOUT'] = "1800"
os.environ['LITELLM_TIMEOUT'] = "1800"
os.environ['OLLAMA_REQUEST_TIMEOUT'] = "1800"
os.environ['OPENAI_TIMEOUT'] = "1800"
os.environ['DEFAULT_TIMEOUT'] = "1800"

# Monkey patch litellm timeout
try:
    import litellm
    litellm.request_timeout = 1800
    litellm.timeout = 1800
    litellm.max_timeout = 1800
    # Override the default timeout in litellm config
    if hasattr(litellm, 'DEFAULT_TIMEOUT'):
        litellm.DEFAULT_TIMEOUT = 1800
except:
    pass

def create_llm(model_key: str):
    """Create an LLM instance with proper timeout configuration"""
    
    model = settings.MODELS[settings.AGENT_MODELS[model_key]]
    
    # Create the LLM with all timeout parameters
    llm = OllamaLLM(
        model=model,
        base_url=settings.OLLAMA_BASE_URL,
        timeout=1800,  # Hardcode to 30 minutes
        request_timeout=1800,
        num_ctx=2048,  # Smaller context for faster processing
        num_batch=128,
        temperature=0.7,
        keep_alive="30m"  # Keep model loaded for 30 minutes
    )
    
    # Try to override internal timeout if accessible
    if hasattr(llm, '_client'):
        if hasattr(llm._client, 'timeout'):
            llm._client.timeout = 1800
    
    return llm