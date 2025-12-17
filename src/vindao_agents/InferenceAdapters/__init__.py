"""Inference adapters for different LLM providers."""

from .InferenceAdapter import InferenceAdapter as InferenceAdapter
from .LiteLLMInferenceAdapter import LiteLLMInferenceAdapter as LiteLLMInferenceAdapter

adapters = {
    "litellm": LiteLLMInferenceAdapter,
}
