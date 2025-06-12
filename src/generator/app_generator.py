"""
Azure OpenAI generator module for Excel Query Bot.

Classes:
    AppGenerator: Azure OpenAI wrapper with retry logic for robust AI interactions.
"""

from __future__ import annotations
from src.generator.base_generator import AbstractGenrator
from langchain_community.chat_models.azure_openai import AzureChatOpenAI
from tenacity import retry, stop_after_attempt, wait_random_exponential
from openai import BadRequestError


class AppGenerator(AbstractGenrator, AzureChatOpenAI):
    """
    Azure OpenAI wrapper with retry logic for robust interactions.

    Attributes:
        azure_endpoint (str): Azure OpenAI service endpoint URL.
        azure_key (str): API key for Azure OpenAI authentication.
        azure_deployment (str): Deployment name of the target GPT model.
        openai_api_version (str): API version for Azure OpenAI service.
        temperature (float): Sampling temperature controlling response randomness (0.0–1.0).
        max_tokens (int): Maximum number of tokens in generated responses.
    """

    def __init__(self: AppGenerator, cfg) -> None:
        """
        Initialize the Azure OpenAI generator with configuration settings.

        Args:
            cfg: Configuration object containing Azure OpenAI settings.
                Expected keys:
                    - GENERATOR.AZURE_ENDPOINT (str)
                    - AZURE.AZURE_GENERATOR_KEY (str)
                    - GENERATOR.AZURE_DEPLOYMENT (str)
                    - GENERATOR.OPENAI_API_VERSION (str)
                    - GENERATOR.TEMPERATURE (float)
                    - GENERATOR.MAX_TOKENS (int)

        """
        azure_endpoint: str = cfg["GENERATOR"]["AZURE_ENDPOINT"]
        azure_key: str = cfg["AZURE"]["AZURE_GENERATOR_KEY"]
        azure_deployment: str = cfg["GENERATOR"]["AZURE_DEPLOYMENT"]
        openai_api_version: str = cfg["GENERATOR"]["OPENAI_API_VERSION"]
        temperature: float = cfg["GENERATOR"]["TEMPERATURE"]
        max_tokens: int = cfg["GENERATOR"]["MAX_TOKENS"]

        super().__init__(
            azure_endpoint=azure_endpoint,
            api_key=azure_key,
            azure_deployment=azure_deployment,
            openai_api_version=openai_api_version,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(10))
    def generate_response(self: AppGenerator, input_text: str) -> str:
        """
        Generate a response using Azure OpenAI with retry logic.

        Args:
            input_text (str): Prompt text to send to the model. Must not be None or empty.

        Returns:
            str: The generated response content, or None if a BadRequestError occurs
                 (e.g., due to prompt filtering or validation failure).

        """
        try:
            if not input_text:
                raise ValueError("Input text cannot be None or empty.")

            response = self.invoke(input_text)
            return response.content

        except BadRequestError:
            return None
