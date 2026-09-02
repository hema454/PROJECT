import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tables import Conversation, Message


async def insert_conversation(session: AsyncSession, tenant_id: uuid.UUID) -> Conversation:
    conversation = Conversation(tenant_id=tenant_id)
    session.add(conversation)
    await session.flush()
    return conversation


async def get_conversation_by_id(
    session: AsyncSession, tenant_id: uuid.UUID, conversation_id: uuid.UUID
) -> Conversation | None:
    result = await session.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.tenant_id == tenant_id,
            Conversation.is_deleted.is_(False),
        )
    )
    return result.scalar_one_or_none()


async def insert_message(
    session: AsyncSession, tenant_id: uuid.UUID, conversation_id: uuid.UUID, role: str, content: str
) -> Message:
    message = Message(tenant_id=tenant_id, conversation_id=conversation_id, role=role, content=content)
    session.add(message)
    await session.flush()
    return message


async def list_messages_for_conversation(
    session: AsyncSession, tenant_id: uuid.UUID, conversation_id: uuid.UUID
) -> list[Message]:
    result = await session.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id, Message.tenant_id == tenant_id)
        .order_by(Message.created_at.asc(), Message.sequence_number.asc())
    )
    return list(result.scalars().all())