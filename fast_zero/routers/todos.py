from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fast_zero.database import get_session
from fast_zero.models import Todo, User
from fast_zero.schemas import (
    FilterTodo,
    Message,
    TodoList,
    TodoPublic,
    TodoSchema,
    TodoUpdate,
)
from fast_zero.security import get_current_user

router = APIRouter(prefix='/todos', tags=['todos'])

Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/', status_code=HTTPStatus.CREATED, response_model=TodoPublic)
async def create_todo(
    current_user: CurrentUser, todo: TodoSchema, session: Session
):
    db_todo = Todo(
        description=todo.description,
        title=todo.title,
        state=todo.state,
        user_id=current_user.id,
    )

    session.add(db_todo)
    await session.commit()
    await session.refresh(db_todo)

    return db_todo


@router.get('/', status_code=HTTPStatus.OK, response_model=TodoList)
async def list_todos(
    current_user: CurrentUser,
    session: Session,
    filter: Annotated[FilterTodo, Query()],
):
    query = select(Todo).where(Todo.user_id == current_user.id)

    if filter.description:
        query = query.filter(Todo.description.contains(filter.description))

    if filter.title:
        query = query.filter(Todo.title.contains(filter.title))

    if filter.state:
        query = query.filter(Todo.state == filter.state)

    todos = await session.scalars(
        query.offset(filter.offset).limit(filter.limit)
    )

    return {'todos': todos.all()}


@router.patch(
    '/{todo_id}', status_code=HTTPStatus.OK, response_model=TodoPublic
)
async def patch_todo(
    todo_id: int,
    current_user: CurrentUser,
    session: Session,
    todo: TodoUpdate,
):
    todo_db = await session.scalar(
        select(Todo).where(Todo.id == todo_id, Todo.user_id == current_user.id)
    )

    if not todo_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Task not found.'
        )

    for key, value in todo.model_dump(exclude_unset=True).items():
        setattr(todo_db, key, value)

    session.add(todo_db)
    await session.commit()
    await session.refresh(todo_db)

    return todo_db


@router.delete('/{todo_id}', status_code=HTTPStatus.OK, response_model=Message)
async def delete_todo(
    session: Session, current_user: CurrentUser, todo_id: int
):
    todo_db = await session.scalar(
        select(Todo).where(Todo.id == todo_id, Todo.user_id == current_user.id)
    )

    if not todo_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Task not found.'
        )

    await session.delete(todo_db)
    await session.commit()

    return {'message': 'Task has been deleted successfully.'}
