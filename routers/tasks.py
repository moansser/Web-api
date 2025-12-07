from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from database import get_db
from models import Task
from schemas import TaskCreate, TaskUpdate, TaskResponse
from routers.websocket import notify_clients

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=List[TaskResponse])
async def get_tasks(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Task).offset(skip).limit(limit).order_by(Task.created_at.desc())
    )
    tasks = result.scalars().all()
    return tasks


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )
    
    return task


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: TaskCreate,
    db: AsyncSession = Depends(get_db)
):
    new_task = Task(
        title=task.title,
        description=task.description,
        completed=task.completed
    )
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    
    await notify_clients(
        message_type="task_created",
        message=f"Task '{new_task.title}' was created",
        data={"task_id": new_task.id, "task": {
            "id": new_task.id,
            "title": new_task.title,
            "completed": new_task.completed
        }}
    )
    
    return new_task


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )
    
    update_data = task_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    
    await db.commit()
    await db.refresh(task)
    
    await notify_clients(
        message_type="task_updated",
        message=f"Task '{task.title}' was updated",
        data={"task_id": task.id, "task": {
            "id": task.id,
            "title": task.title,
            "completed": task.completed
        }}
    )
    
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )
    
    task_title = task.title
    await db.delete(task)
    await db.commit()
    
    await notify_clients(
        message_type="task_deleted",
        message=f"Task '{task_title}' was deleted",
        data={"task_id": task_id}
    )
    
    return None

