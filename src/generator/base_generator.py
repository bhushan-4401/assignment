"""Abstract base class module for response generators.

Classes:
    AbstractGenrator: Abstract base class for response generation implementations.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class AbstractGenrator(ABC):
    """Abstract base class defining the interface for response generation.

    This class establishes a common contract for all response generators in the
    Excel Query Bot application. It ensures that different language model
    implementations (Azure OpenAI, local models, etc.) provide consistent
    interfaces for text generation operations.

    """

    @abstractmethod
    def generate_response(self: AbstractGenrator, input_text: str) -> str:
        """Generate a response for the given input text.

        This abstract method must be implemented by all concrete generator classes
        to provide text generation functionality. The method should process the
        input text and return an appropriate response based on the specific
        language model or generation strategy used by the implementation.

        Args:
            input_text (str): The input text prompt for which a response needs
                to be generated. Should not be None or empty.

        Returns:
            str: The generated response text for the given input prompt.
                The format and content depend on the specific implementation.

        """
