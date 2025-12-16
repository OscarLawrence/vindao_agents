"""Inference adapters for different LLM providers."""

from .InferenceAdapter import InferenceAdapter
from .LiteLLMInferenceAdapter import LiteLLMInferenceAdapter

adapters = {
    "litellm": LiteLLMInferenceAdapter,
}
