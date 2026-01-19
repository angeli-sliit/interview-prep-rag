from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
import os

def get_llm(provider="groq", api_key=None, model_name=None):
    """Get LLM instance"""
    if provider == "groq":
        api_key = api_key or os.getenv("GROQ_API_KEY")
        model_name = model_name or "llama-3.1-8b-instant"
        return ChatGroq(
            groq_api_key=api_key,
            model_name=model_name,
            temperature=0.7
        )
    elif provider == "openai":
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        model_name = model_name or "gpt-3.5-turbo"
        return ChatOpenAI(
            openai_api_key=api_key,
            model_name=model_name,
            temperature=0.7
        )
    else:
        raise ValueError(f"Unsupported provider: {provider}")

def get_prompt_template(answer_mode="default", length="medium"):
    """Get prompt template based on answer mode"""
    
    base_template = """You are an expert interview preparation assistant. Your role is to help candidates prepare for job interviews by providing structured, role-specific answers based on the job description and interview materials provided.

Use the following context from the job description and interview materials to answer the question. Structure your answer professionally and clearly.

Context:
{context}

Question: {question}

{format_instructions}

Answer:"""
    
    format_instructions_map = {
        "star": """Provide your answer using the STAR method (Situation, Task, Action, Result):
- **Situation**: Set the context
- **Task**: Describe what needed to be done
- **Action**: Explain what you did
- **Result**: Share measurable outcomes

Ensure your answer:
1. Is specific to the role and company mentioned in the context
2. Includes quantifiable results/metrics
3. Demonstrates relevant skills and experiences""",
        
        "bullet": """Provide your answer using clear bullet points:
- Use concise, impactful statements
- Each bullet should highlight a key point
- Include specific examples from the context
- Demonstrate relevant skills and experiences""",
        
        "default": """Provide a well-structured answer that:
1. Is specific to the role and company mentioned in the context
2. Uses clear bullet points or the STAR method (Situation, Task, Action, Result) when appropriate
3. Demonstrates relevant skills and experiences
4. Is concise but comprehensive"""
    }
    
    length_instructions = {
        "short": "Keep your answer brief and to the point (2-3 sentences or 3-4 bullet points).",
        "medium": "Provide a comprehensive answer with adequate detail.",
        "long": "Provide a detailed, thorough answer with extensive examples and explanations."
    }
    
    format_instruction = format_instructions_map.get(answer_mode, format_instructions_map["default"])
    length_instruction = length_instructions.get(length, "")
    
    if length_instruction:
        format_instruction = f"{format_instruction}\n\n{length_instruction}"
    
    return base_template.replace("{format_instructions}", format_instruction)

def create_qa_chain(llm, vectorstore, answer_mode="default", length="medium"):
    """Create RAG QA chain with custom prompt"""
    prompt_template = get_prompt_template(answer_mode, length)

    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"]
    )
    
    # Create retriever with similarity scores
    retriever = vectorstore.as_retriever(
        search_kwargs={"k": 3}
    )
    
    # Create a simple chain class that mimics RetrievalQA
    class QAClass:
        def __init__(self, llm, retriever, prompt, vectorstore):
            self.llm = llm
            self.retriever = retriever
            self.prompt = prompt
            self.vectorstore = vectorstore
            
        def __call__(self, inputs):
            query = inputs.get("query", "")
            chat_history = inputs.get("chat_history", "")
            
            # Retrieve relevant documents
            docs = self.retriever.invoke(query)
            
            # Get similarity scores using similarity_search_with_score
            try:
                # Use the vectorstore directly to get scores
                docs_with_scores = self.vectorstore.similarity_search_with_score(
                    query, k=len(docs)
                )
                # Extract docs and convert distance to similarity (0-1)
                docs = [doc for doc, score in docs_with_scores]
                scores = [max(0, min(1, 1 - score)) for _, score in docs_with_scores]
            except Exception as e:
                # Fallback if scores not available
                scores = [0.85, 0.80, 0.75][:len(docs)]  # Placeholder scores
            
            # Combine context from documents
            context = "\n\n".join([doc.page_content for doc in docs])
            
            # Add chat history if provided
            if chat_history:
                full_query = f"Previous conversation:\n{chat_history}\n\nCurrent question: {query}"
            else:
                full_query = query
            
            # Format prompt
            formatted_prompt = self.prompt.format(context=context, question=full_query)
            
            # Generate answer (handle ChatGroq and ChatOpenAI message format)
            try:
                if hasattr(self.llm, 'invoke'):
                    # For ChatGroq/ChatOpenAI, use HumanMessage format
                    from langchain_core.messages import HumanMessage
                    messages = [HumanMessage(content=formatted_prompt)]
                    answer = self.llm.invoke(messages)
                    # Extract content if it's a message object
                    if hasattr(answer, 'content'):
                        answer = answer.content
                    else:
                        answer = str(answer)
                else:
                    # Fallback for string-based LLMs
                    answer = str(self.llm(formatted_prompt))
            except Exception as e:
                # Fallback: try direct invoke with string
                try:
                    answer = str(self.llm.invoke(formatted_prompt))
                except:
                    answer = f"Error generating answer: {str(e)}"
            
            return {
                "result": str(answer),
                "source_documents": docs,
                "similarity_scores": scores
            }
    
    return QAClass(llm, retriever, prompt, vectorstore)
