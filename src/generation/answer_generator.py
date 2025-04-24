# This module will contain the RAG chain logic. 

from langchain_community.vectorstores import VectorStore
from langchain_core.language_models import BaseLanguageModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda, RunnableParallel
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import logging
import os
from typing import List, Optional, Dict, Union

load_dotenv() # Load environment variables from .env file

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
    return "\n\n".join(doc.page_content for doc in docs)


def create_rag_chain(retriever: VectorStore, llm: BaseLanguageModel):
    """Creates the RAG chain using LangChain Expression Language (LCEL).
    
    Returns a chain that expects a query string and returns a dictionary
    containing 'context', 'question', and 'answer'.
    """
    # Use ChatPromptTemplate for chat models
    prompt = ChatPromptTemplate.from_template(RAG_PROMPT_TEMPLATE)

    # Sub-chain to retrieve documents and format them
    # retriever argument here is the retriever interface (e.g., obtained via .as_retriever())
    retrieve_docs_chain = RunnableLambda(lambda input_query: retriever.invoke(input_query))

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

    # The final chain now returns {'documents': List[Document], 'question': str, 'answer': str}
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
    try:
        # Initialize the LLM (requires OPENAI_API_KEY environment variable)
        llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)

        # Get the retriever interface from the vector store
        # Note: The `create_rag_chain` function now expects the retriever interface directly
        retriever_interface = retriever # Assuming the passed retriever IS the interface

        # Create the RAG chain using the interface
        rag_chain = create_rag_chain(retriever_interface, llm)

        # Invoke the chain to get the result dictionary
        logging.info(f"Invoking RAG chain for query: {query[:50]}...")
        result_dict = rag_chain.invoke(query)
        logging.info("RAG chain invocation successful.")

        answer_str = result_dict.get("answer")
        retrieved_docs = result_dict.get("documents", [])

        # Format sources
        formatted_sources = set() # Use a set to store unique sources
        for doc in retrieved_docs:
            metadata = doc.metadata
            source_path = metadata.get("source")
            page = metadata.get("page")
            
            if source_path:
                source_name = os.path.basename(source_path)
                if page is not None: # Check if page number exists
                    formatted_sources.add(f"Source: {source_name}, Page {page}")
                else:
                    formatted_sources.add(f"Source: {source_name}") # Format without page if missing
            # Optionally handle cases where source_path is missing

        return {"answer": answer_str, "sources": sorted(list(formatted_sources))}

    except Exception as e:
        logging.exception(f"Error generating answer for query: {query[:50]}...")
        return {"answer": None, "sources": []} 