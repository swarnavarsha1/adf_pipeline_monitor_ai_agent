"""
RAGSolutionRetriever
Given a failure rationale, searches the FAISS index built from your PDFs and uses GPT to suggest a solution.
"""

import os
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config import OPENAI_API_KEY

INDEX_DIR = os.path.join(os.path.dirname(__file__), "faiss_index")

PROMPT_TEMPLATE = """You are an Azure Data Factory troubleshooting assistant.
Given this failure reason from a pipeline run:
---
{failure_reason}
---
and the following retrieved documentation:
---
{context}
---
Provide a direct, actionable, step-by-step solution based ONLY on the above documentation.
If no relevant solution is in the documentation, reply exactly: 'No documented solution found.'
"""

class RAGSolutionRetriever:
    def __init__(self, top_k=3, model_name="gpt-4o"):
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not set in environment or config.py")

        # Load index and retriever
        embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
        self.vectorstore = FAISS.load_local(INDEX_DIR, embeddings, allow_dangerous_deserialization=True)
        self.retriever = self.vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": top_k})

        # Setup LLM & prompt
        self.llm = ChatOpenAI(model_name=model_name, temperature=0, api_key=OPENAI_API_KEY)
        self.prompt = PromptTemplate.from_template(PROMPT_TEMPLATE)
        self.parser = StrOutputParser()

    def get_solution(self, failure_reason: str) -> str:
        """Retrieve and summarize a solution for the given failure reason."""
        if not failure_reason.strip():
            return "No documented solution found."

        # Get top_k relevant chunks from the vector store
        docs = self.retriever.invoke(failure_reason)
        if not docs:
            return "No documented solution found."

        # Format retrieved docs for prompt
        context = "\n\n---\n\n".join(
            [f"Source: {d.metadata.get('source_file', 'Unknown')}\n{d.page_content}" for d in docs]
        )

        # Prepare final prompt
        prompt_msg = self.prompt.invoke({"failure_reason": failure_reason, "context": context})

        # Get response from LLM
        response = self.llm.invoke(prompt_msg)
        return self.parser.invoke(response)
