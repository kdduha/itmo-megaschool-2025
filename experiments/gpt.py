import openai
import json
from typing import List, Dict, Any


class OpenAIClientError(Exception):
    """Exception raised for errors in OpenAIClient."""
    pass


class OpenAIClient:
    """
    A custom client for interacting with the OpenAI API, enforcing structured JSON responses.

    This client provides methods for sending chat completion requests to the OpenAI API, ensuring that responses are in a
    structured JSON format, which can be further processed according to custom schemas.

    Methods
    -------
    chat_completion(message: str, model: str) -> Dict[str, Any]
        Sends a chat completion request and returns the structured JSON response.
    """

    def __init__(self, api_key: str, base_url: str, system_prompt: str) -> None:
        """
        Initializes the OpenAIClient with the provided API key, base URL, and system prompt.

        Parameters
        ----------
        api_key : str
            The API key for authenticating requests to the OpenAI API.
        base_url : str
            The base URL for the OpenAI API endpoint.
        system_prompt : str
            The system message to guide the model's responses.
        """
        self._api_key = api_key
        self._base_url = base_url
        self._system_prompt = system_prompt
        self._client = openai.OpenAI(
            api_key=self._api_key,
            base_url=self._base_url,
        )

    def chat_completion(self, message: str, model: str) -> Dict[str, Any]:
        """
        Sends a chat completion request to the OpenAI API and returns the structured JSON response.

        Parameters
        ----------
        message : str
            The user message to send to the model. This message will be part of the chat context.
        model : str
            The model to use for generating the response (e.g., "gpt-4").

        Returns
        -------
        Dict[str, Any]
            A dictionary containing the parsed JSON response from the model.

        Raises
        ------
        OpenAIClientError
            If the API request fails or if the response cannot be parsed as JSON.
        json.JSONDecodeError
            If the response from the model cannot be decoded as a valid JSON object.
        Exception
            If any other unexpected errors occur during the request.
        """
        full_message = [
            {"role": "system", "content": self._system_prompt},
            {"role": "user", "content": message}
        ]

        try:
            response = self._client.chat.completions.create(
                model=model,
                messages=full_message,
            )

            response_text = response.choices[0].message.content
            parsed_response = json.loads(response_text)
            return parsed_response

        except json.JSONDecodeError:
            raise OpenAIClientError("Failed to parse model response as JSON.")
        except Exception as e:
            raise OpenAIClientError(f"Unexpected error during OpenAI API request: {str(e)}")
