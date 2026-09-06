from citations import extract_citations
from context_manager import add_turn, get_history
from llm_client import chat
from models import AnswerResponse
from prompt import build_prompt
from refusal import check_refusal
from retriever import retrieve


def answer_question(question: str, conversation_id: str) -> AnswerResponse:
    chunks = retrieve(question)
    refused, refusal_text = check_refusal(chunks)
    if refused:
        return AnswerResponse(answer=refusal_text, citations=[], refused=True)

    history = get_history(conversation_id)
    messages = build_prompt(question, chunks, history)
    raw_answer = chat(messages)
    citations = extract_citations(raw_answer, chunks)

    if not citations:
        # model produced no valid citation against retrieved context -> treat as refusal
        return AnswerResponse(
            answer="I don't know based on the provided documents.",
            citations=[],
            refused=True,
        )

    add_turn(conversation_id, question, raw_answer)
    return AnswerResponse(answer=raw_answer, citations=citations, refused=False)