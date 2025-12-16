"""Inference adapters for different LLM providers."""

from .LiteLLMInferenceAdapter import LiteLLMInferenceAdapter
from .InferenceAdapter import InferenceAdapter

adapters = {
    "litellm": LiteLLMInferenceAdapter,
}