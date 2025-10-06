from dataclasses import asdict

import pytest
from sqlalchemy import select

from fast_zero.models import Todo, User


@pytest.mark.asyncio
async def test_create_user(session, mock_db_time):
    with mock_db_time(model=User) as time:
        new_user = User(username='alice', password='secret', email='test@test')
        session.add(new_user)
        await session.commit()

    found_user = await session.scalar(
        select(User).where(User.username == 'alice')
    )

    assert asdict(found_user) == {
        'id': 1,
        'username': 'alice',
        'password': 'secret',
        'email': 'test@test',
        'created_at': time,
        'todos': [],
    }


@pytest.mark.asyncio
async def test_create_todo(session, user: User):
    new_todo = Todo(
        title='Test Todo',
        description='Test Desc',
        state='draft',
        user_id=user.id,
    )

    session.add(new_todo)
    await session.commit()

    found_todo = await session.scalar(select(Todo))

    assert asdict(found_todo) == {
        'id': 1,
        'title': 'Test Todo',
        'description': 'Test Desc',
        'state': 'draft',
        'user_id': user.id
    }


@pytest.mark.asyncio
async def test_user_todo_relationship(session, user: User):
    todo = Todo(
        title='Test todo',
        description='Test Desc',
        state='draft',
        user_id=user.id
    )

    session.add(todo)
    await session.commit()
    await session.refresh(user)

    user: User = await session.scalar(select(User).where(User.id == user.id))

    assert user.todos == [todo]
