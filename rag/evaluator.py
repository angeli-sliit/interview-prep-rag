from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage

def evaluate_answer(llm, question, answer, context=""):
    """Evaluate answer quality and provide feedback"""
    
    evaluation_prompt = """You are an expert interview coach evaluating an interview answer. Rate the answer on three criteria (0-10 scale) and provide specific feedback.

Question: {question}

Answer to Evaluate:
{answer}

Context Used (if available):
{context}

Evaluate the answer on:
1. **Relevance** (0-10): How well does the answer address the question? Is it specific to the role/context?
2. **Clarity** (0-10): Is the answer clear, well-structured, and easy to follow?
3. **STAR Completeness** (0-10): Does it follow STAR method (Situation, Task, Action, Result) when appropriate? Does it include measurable results?

Provide your evaluation in this EXACT format:
SCORE_RELEVANCE: [0-10]
SCORE_CLARITY: [0-10]
SCORE_STAR: [0-10]
FEEDBACK: [Your detailed feedback with specific strengths and areas for improvement, using ✔ for strengths and ✖ for weaknesses]
OVERALL_SCORE: [Average of three scores, rounded to 1 decimal]

Be specific and actionable in your feedback."""

    try:
        prompt = evaluation_prompt.format(
            question=question,
            answer=answer,
            context=context[:500] if context else "No context provided"
        )
        
        if hasattr(llm, 'invoke'):
            messages = [HumanMessage(content=prompt)]
            response = llm.invoke(messages)
            if hasattr(response, 'content'):
                response_text = response.content
            else:
                response_text = str(response)
        else:
            response_text = str(llm(prompt))
        
        # Parse the response
        scores = {
            "relevance": 0,
            "clarity": 0,
            "star": 0,
            "overall": 0,
            "feedback": ""
        }
        
        lines = response_text.split('\n')
        feedback_lines = []
        in_feedback = False
        
        for line in lines:
            line = line.strip()
            if line.startswith("SCORE_RELEVANCE:"):
                try:
                    scores["relevance"] = float(line.split(":")[1].strip())
                except:
                    pass
            elif line.startswith("SCORE_CLARITY:"):
                try:
                    scores["clarity"] = float(line.split(":")[1].strip())
                except:
                    pass
            elif line.startswith("SCORE_STAR:"):
                try:
                    scores["star"] = float(line.split(":")[1].strip())
                except:
                    pass
            elif line.startswith("OVERALL_SCORE:"):
                try:
                    scores["overall"] = float(line.split(":")[1].strip())
                except:
                    pass
            elif line.startswith("FEEDBACK:"):
                in_feedback = True
                feedback_lines.append(line.replace("FEEDBACK:", "").strip())
            elif in_feedback and line:
                feedback_lines.append(line)
        
        scores["feedback"] = "\n".join(feedback_lines) if feedback_lines else "Evaluation completed."
        
        # Calculate overall if not provided
        if scores["overall"] == 0:
            scores["overall"] = round((scores["relevance"] + scores["clarity"] + scores["star"]) / 3, 1)
        
        return scores
        
    except Exception as e:
        return {
            "relevance": 0,
            "clarity": 0,
            "star": 0,
            "overall": 0,
            "feedback": f"Error during evaluation: {str(e)}"
        }
