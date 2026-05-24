from openai import OpenAI

from app.config import settings


client = OpenAI(api_key=settings.openai_api_key)


## RAG (Retrieval-Augmented Generation) service to generate answers based on retrieved document chunks
def generate_answer(question: str, context_chunks: list[dict]) -> str:
    if not question:
        raise ValueError("Question cannot be empty.")
    
    if not context_chunks:
        return "I could not find relevant information in the uploaded documents."
    
    context_text = "\n\n".join(
        [
            f"[Source {index + 1}: {chunk['filename']}, chunk {chunk['chunk_index']}]\n{chunk['content']}"
            for index, chunk in enumerate(context_chunks)
        ]
    )

    prompt = f"""
Your job is to answer the user's question using ONLY the provided document excerpts.

Rules:
1. Use only information found in the document excerpts.
2. Do not use outside knowledge.
3. If the excerpts do not contain the answer, say exactly:
   "I could not find that information in the uploaded documents."
4. Cite sources using [Source 1], [Source 2], etc.
5. Do not offer follow-up help.
6. Do not say "if you want" or suggest additional tasks.
7. Keep the answer concise unless the question asks for detail.
8. If listing items, use a clean bullet list.
9. Do not mention sources that do not support the specific claim.
10. Do not invent missing details.

Document excerpts:
{context_text}

Question:
{question}
"""
    
    response = client.responses.create(
        model=settings.openai_chat_model,
        input=prompt
    )

    return response.output_text

