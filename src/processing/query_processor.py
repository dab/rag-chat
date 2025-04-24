# src/processing/query_processor.py

import logging
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompt_values import ChatPromptValue

# Get logger instance using standard practice
logger = logging.getLogger(__name__)

def process_query(query: str) -> str:
    """Processes the raw user query using LangChain prompt template.

    Args:
        query: The raw query string from the user.

    Returns:
        The formatted prompt string.

    Raises:
        ValueError: If the query is empty or None after stripping.
        RuntimeError: If LangChain prompt invocation fails.
    """
    logger.debug(f"Received raw query: '{query[:100]}...'")
    # Check for None explicitly first
    if query is None:
        logger.error("Received None query.") # Changed level to error
        raise ValueError("Query cannot be None.")

    processed_query = query.strip()

    # Now check if empty after stripping
    if not processed_query:
        logger.error("Query is empty or became empty after stripping whitespace.") # Changed level to error
        raise ValueError("Query cannot be empty after stripping.")

    logger.info(f"Processing query: '{processed_query[:100]}...'") # Use logger consistently

    # --- LangChain Integration --- 
    # Note: This uses a basic prompt, not the full RAG chain yet
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant."),
        ("human", "{user_input}")
    ])

    # Invoke the prompt template with the processed query
    try:
        logger.debug("Invoking LangChain prompt template...")
        prompt_value: ChatPromptValue = prompt.invoke({"user_input": processed_query})
        # Convert the ChatPromptValue to a string representation
        formatted_output = prompt_value.to_string()
        logger.info(f"LangChain formatted query output generated.")
        logger.debug(f"LangChain formatted output snippet: \n{formatted_output[:200]}...") # Log snippet
        return formatted_output
    except Exception as e:
        logger.exception("Error invoking LangChain prompt template.") # Use logger.exception
        # Fallback or re-raise depending on desired behavior
        # For now, re-raise as a general exception to be caught upstream
        raise RuntimeError(f"Failed to format query using LangChain: {e}")

    # # Return the processed string to maintain compatibility with current simple usage
    # # TODO: Replace this with actual LangChain chain invocation later
    # return processed_query # Original return removed 