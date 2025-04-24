# src/processing/query_processor.py

import logging
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompt_values import ChatPromptValue

logger = logging.getLogger(__name__)

def process_query(query: str) -> str:
    """Processes the raw user query.

    Args:
        query: The raw query string from the user.

    Returns:
        The processed query string.

    Raises:
        ValueError: If the query is empty or None after stripping.
    """
    # Check for None explicitly first
    if query is None:
        logger.warning("Received None query.")
        raise ValueError("Query cannot be None.")

    processed_query = query.strip()

    # Now check if empty after stripping
    if not processed_query:
        logger.warning("Query is empty or became empty after stripping whitespace.")
        raise ValueError("Query cannot be empty after stripping.")

    logger.info(f"Processed query: '{processed_query}'")

    # --- LangChain Integration --- 
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant."),
        ("human", "{user_input}")
    ])
    
    # Invoke the prompt template with the processed query
    try:
        prompt_value: ChatPromptValue = prompt.invoke({"user_input": processed_query})
        # Convert the ChatPromptValue to a string representation
        formatted_output = prompt_value.to_string()
        logger.info(f"LangChain formatted output: \n{formatted_output}")
        return formatted_output
    except Exception as e:
        logger.exception(f"Error invoking LangChain prompt: {e}")
        # Fallback or re-raise depending on desired behavior
        # For now, re-raise as a general exception to be caught upstream
        raise RuntimeError(f"Failed to format query using LangChain: {e}")

    # # Return the processed string to maintain compatibility with current simple usage
    # # TODO: Replace this with actual LangChain chain invocation later
    # return processed_query # Original return removed 