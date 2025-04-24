# This module will contain the RAG chain logic.

import logging # Added import
import os
from typing import List, Dict, Union

from langchain_community.vectorstores import VectorStore # Keep specific type hint
from langchain_core.language_models import BaseLanguageModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda, RunnableParallel
from langchain_openai import ChatOpenAI
# from dotenv import load_dotenv # Removed dotenv import

# load_dotenv() # Removed call - handled centrally

# Get logger instance using standard practice
logger = logging.getLogger(__name__)

# Template for prompting the LLM
# Updated template to be more specific about using only provided context
RAG_PROMPT_TEMPLATE = """
CONTEXT:
{context}

QUESTION:
{question}

Answer the QUESTION based *only* on the provided CONTEXT. If the context doesn't contain the answer, state that you cannot answer based on the provided information.
"""

def format_docs(docs):
    # Adding a simple log here, might be verbose if called often
    logger.debug(f"Formatting {len(docs)} documents for context.")
    return "\n\n".join(doc.page_content for doc in docs)

def create_rag_chain(retriever: VectorStore, llm: BaseLanguageModel):
    """Creates the RAG chain using LangChain Expression Language (LCEL).

    Returns a chain that expects a query string and returns a dictionary
    containing 'context', 'question', and 'answer'.
    """
    logger.info("Creating RAG chain...")
    # Use ChatPromptTemplate for chat models
    prompt = ChatPromptTemplate.from_template(RAG_PROMPT_TEMPLATE)

    # Sub-chain to retrieve documents and format them
    # retriever argument here is the retriever interface (e.g., obtained via .as_retriever())
    retrieve_docs_chain = RunnableLambda(lambda input_query: retriever.invoke(input_query))
    logger.debug("RAG chain: Defined document retrieval sub-chain.")

    # Chain to process the retrieved documents and generate the answer
    rag_chain_from_docs = (
        {
            "context": lambda x: format_docs(x["documents"]),
            "question": lambda x: x["question"],
        }
        | prompt
        | llm
        # No StrOutputParser here, as we want the AIMessage or dict from the LLM potentially
        # But for now, assuming llm directly gives string or AIMessage convertible by StrOutputParser
        | StrOutputParser() # Keep StrOutputParser for now to ensure answer is string
    )
    logger.debug("RAG chain: Defined core doc processing and LLM call sub-chain.")

    # Final chain using RunnableParallel and assign
    # It takes the original query (passed as input)
    # Runs retrieval and question passthrough in parallel
    # Then assigns the generated answer based on the retrieved docs and question
    final_chain = RunnableParallel(
        {
            "documents": retrieve_docs_chain,
            "question": RunnablePassthrough()
        }
    ).assign(answer=rag_chain_from_docs)
    logger.debug("RAG chain: Defined final parallel execution structure.")

    # The final chain now returns {'documents': List[Document], 'question': str, 'answer': str}
    logger.info("RAG chain created successfully.")
    return final_chain

def generate_answer(query: str, retriever: VectorStore) -> Dict[str, Union[str, List[str], None]]:
    """Generates an answer using the RAG chain and includes source attribution.

    Args:
        query: The user's query string.
        retriever: The vector store retriever interface.

    Returns:
        A dictionary containing:
        - "answer" (str | None): The generated answer string, or None if an error occurred.
        - "sources" (List[str]): A list of formatted source attribution strings.
    """
    logger.info(f"Generating answer for query: '{query[:100]}...'") # Use logger
    try:
        # Initialize the LLM (requires OPENAI_API_KEY environment variable)
        # Check if the correct API key exists 
        api_key = os.getenv("OPENAI_API_KEY") # Corrected to use OPENAI_API_KEY
        if not api_key:
            logger.error("OPENAI_API_KEY not found in environment variables.") # Corrected log message
            # Optionally check for LANGCHAIN_API_KEY for LangSmith tracing here if needed
            raise ValueError("Missing OPENAI_API_KEY for LLM initialization.") # Corrected error message

        logger.debug("Initializing ChatOpenAI LLM (gpt-3.5-turbo)...")
        # Explicitly pass the OPENAI key 
        llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0, api_key=api_key) 
        logger.debug("LLM initialized.")

        # Get the retriever interface from the vector store
        # Note: The `create_rag_chain` function now expects the retriever interface directly
        retriever_interface = retriever # Assuming the passed retriever IS the interface
        logger.debug("Retriever interface confirmed.")

        # Create the RAG chain using the interface
        rag_chain = create_rag_chain(retriever_interface, llm)

        # Invoke the chain to get the result dictionary
        logger.info(f"Invoking RAG chain...") # Use logger
        result_dict = rag_chain.invoke(query)
        logger.info("RAG chain invocation successful.") # Use logger
        logger.debug(f"RAG chain result keys: {result_dict.keys()}")

        answer_str = result_dict.get("answer")
        retrieved_docs = result_dict.get("documents", [])
        logger.debug(f"Answer generated (snippet): '{answer_str[:100]}...'")
        logger.debug(f"Retrieved {len(retrieved_docs)} documents for context.")

        # Format sources
        formatted_sources = set() # Use a set to store unique sources
        for i, doc in enumerate(retrieved_docs):
            metadata = doc.metadata
            source_path = metadata.get("source")
            page = metadata.get("page")
            logger.debug(f"Processing source doc {i+1}: Path='{source_path}', Page={page}")

            if source_path:
                source_name = os.path.basename(source_path)
                if page is not None: # Check if page number exists
                    source_str = f"Source: {source_name}, Page {page}"
                    formatted_sources.add(source_str)
                    logger.debug(f"Added source: {source_str}")
                else:
                    source_str = f"Source: {source_name}"
                    formatted_sources.add(source_str) # Format without page if missing
                    logger.debug(f"Added source (no page): {source_str}")
            else:
                logger.warning(f"Source document {i+1} missing 'source' metadata.")
            # Optionally handle cases where source_path is missing

        final_sources = sorted(list(formatted_sources))
        logger.info(f"Formatted {len(final_sources)} unique sources.")
        return {"answer": answer_str, "sources": final_sources}

    except Exception:
        logger.exception(f"Error generating answer for query: '{query[:100]}...'") # Use logger
        return {"answer": "An error occurred while generating the answer.", "sources": []} # Provide error message in answer