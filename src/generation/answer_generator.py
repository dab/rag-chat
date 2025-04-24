# This module will contain the RAG chain logic. 

from langchain_community.vectorstores import VectorStore
from langchain_core.language_models import BaseLanguageModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

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
    """Creates the RAG chain using LangChain Expression Language (LCEL)."""

    # Use ChatPromptTemplate for chat models
    prompt = ChatPromptTemplate.from_template(RAG_PROMPT_TEMPLATE)

    # Define a step to invoke retriever and format docs
    def retrieve_and_format(input_query):
        docs = retriever.invoke(input_query)
        return format_docs(docs)

    rag_chain = (
        # Pass the question through, and retrieve/format context based on the question
        {"context": RunnableLambda(retrieve_and_format), "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain


def generate_answer(query: str, retriever: VectorStore):
    """Generates an answer using the RAG chain."""
    # Initialize the LLM (requires OPENAI_API_KEY environment variable)
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)

    # Get the retriever interface from the vector store
    retriever_interface = retriever.as_retriever()

    # Create the RAG chain using the interface
    rag_chain = create_rag_chain(retriever_interface, llm)

    # Invoke the chain to get the answer
    answer = rag_chain.invoke(query)
    return answer 