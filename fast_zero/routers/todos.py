from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from fast_zero.models import Todo
from fast_zero.models import User

from fast_zero.database import get_session
from fast_zero.schemas import TodoPublic, TodoSchema

from fast_zero.security import get_current_user

router = APIRouter(prefix='/todos', tags=['todos'])

Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]

@router.post ('/', status_code=HTTPStatus.CREATED, response_model=TodoPublic)
async def create_todo(current_user: CurrentUser, todo: TodoSchema, session: Session):
    db_todo = Todo(
        description=todo.description,
        title=todo.title,
        state=todo.state,
        user_id=current_user,
    )

    session.add(db_todo)
    await session.commit()
    await session.refresh(db_todo)

    return db_todo
