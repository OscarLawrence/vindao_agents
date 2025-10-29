"""Inference adapters for different LLM providers."""

from .LiteLLMInferenceAdapter import LiteLLMInferenceAdapter

adapters = {
    "litellm": LiteLLMInferenceAdapter,
}