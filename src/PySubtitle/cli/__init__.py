# CLI entry points for gpt-subtrans package
from .azure import main as azure_main
from .bedrock import main as bedrock_main
from .claude import main as claude_main
from .deepseek import main as deepseek_main
from .gemini import main as gemini_main
from .gpt import main as gpt_main
from .llm import main as llm_main
from .mistral import main as mistral_main

__all__ = [
    'azure_main',
    'bedrock_main',
    'claude_main',
    'deepseek_main',
    'gemini_main',
    'gpt_main',
    'llm_main',
    'mistral_main'
]
