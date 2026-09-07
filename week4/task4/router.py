from fastapi import APIRouter

from models import AnswerResponse, QueryRequest
from service import answer_question

router = APIRouter()


@router.post("/ask", response_model=AnswerResponse)
def ask(request: QueryRequest):
    return answer_question(request.question, request.conversation_id)