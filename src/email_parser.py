"""
Email parsing agent that uses Ollama (llama3.2) to extract structured information from raw emails.

The agent works in the following way:
1. Takes a raw email string as input
2. Uses a language model prompt to guide extraction of key fields
3. Parses the model's JSON response into a structured format
4. Returns a validated data model with all extracted information
"""

import json
import os
from typing import Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate

from .prompts import EMAIL_PARSING_PROMPT


# Load environment variables (for future extensibility - API keys, etc.)
load_dotenv()


class EmailData(BaseModel):
    """
    Structured representation of parsed email data.

    This Pydantic model ensures type safety and validation of the extracted fields.
    Pydantic will raise errors if the data doesn't match expected types.
    """
    sender: str = Field(description="Email address or name of sender")
    subject: str = Field(description="Email subject line")
    date: Optional[str] = Field(default=None, description="Date email was sent")
    main_intent: str = Field(description="Primary purpose of the email")
    action_items: list[str] = Field(default_factory=list, description="Tasks/actions requested")
    urgency_level: str = Field(description="Urgency: 'high', 'medium', or 'low'")


class EmailParserAgent:
    """
    Agent for parsing emails using Ollama and LangChain.

    Components:
    - OllamaLLM: Calls the local Ollama instance running llama3.2
    - PromptTemplate: Formats the prompt with email text
    - LLMChain: Chains the prompt template with the LLM

    The agent extracts structured information from unstructured email text.
    """

    def __init__(self, model_name: str = "llama3.2", ollama_base_url: str = "http://localhost:11434"):
        """
        Initialize the email parser agent.

        Args:
            model_name: Name of the Ollama model to use (default: llama3.2)
            ollama_base_url: URL where Ollama server is running (default: http://localhost:11434)
        """
        # Initialize the language model
        # OllamaLLM connects to the local Ollama instance
        # num_predict=500 limits output length to reduce processing time
        self.llm = OllamaLLM(
            model=model_name,
            base_url=ollama_base_url,
            num_predict=500,
            temperature=0.3  # Lower temperature for more consistent/factual outputs
        )

        # Create the prompt template
        # PromptTemplate takes a template string and variable names
        # When we call .format(email_text="..."), it substitutes the variables
        self.prompt_template = PromptTemplate(
            input_variables=["email_text"],
            template=EMAIL_PARSING_PROMPT
        )

        # Chain the prompt with the LLM using pipe operator
        # This creates: prompt -> format with input -> send to LLM -> get output
        self.chain = self.prompt_template | self.llm

    def parse_email(self, email_text: str) -> EmailData:
        """
        Parse a raw email and extract structured information.

        Process:
        1. Run the chain with the email text (invokes LLM with the prompt)
        2. Extract JSON from the response (LLM output)
        3. Parse JSON into a Python dictionary
        4. Validate against EmailData model (ensures correct types/fields)
        5. Return the validated EmailData object

        Args:
            email_text: Raw email content as a string

        Returns:
            EmailData: Structured email data with validated fields

        Raises:
            json.JSONDecodeError: If LLM response is not valid JSON
            ValueError: If extracted data doesn't match expected schema
        """
        # Invoke the chain - this sends the prompt to Ollama and gets a response
        response = self.chain.invoke({"email_text": email_text})

        # Extract the text from the response
        # OllamaLLM returns a string directly, not an AIMessage
        response_text = response if isinstance(response, str) else response.content

        # Clean up the response: remove markdown code blocks if present
        # Sometimes LLMs wrap JSON in ```json ... ``` blocks
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]

        response_text = response_text.strip()

        # Parse the JSON response into a dictionary
        parsed_data = json.loads(response_text)

        # Validate and create EmailData object
        # Pydantic will raise errors if data is invalid
        email_data = EmailData(**parsed_data)

        return email_data


def parse_email(email_text: str) -> EmailData:
    """
    Convenience function to parse an email with default settings.

    Creates an agent with default configuration and parses the email.

    Args:
        email_text: Raw email content

    Returns:
        EmailData: Parsed and validated email data
    """
    agent = EmailParserAgent()
    return agent.parse_email(email_text)
