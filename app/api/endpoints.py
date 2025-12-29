import logging
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.exceptions import HTTPException
from starlette.status import HTTP_404_NOT_FOUND, HTTP_204_NO_CONTENT

from app.api.schemas import SourceResponse, SourceCreate, SourceUpdate, PostResponse
from app.database import get_db, Source, Post

logger = logging.getLogger(__name__)

router = APIRouter(prefix='/api', tags=['api'])


@router.get('/sources/', response_model=List[SourceResponse])
async def get_sources(
        offset: int = 0,
        limit: int = 20,
        db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Source).offset(offset).limit(limit))
    sources = result.scalars().all()
    return sources

@router.get('/posts/', response_model=List[PostResponse])
async def get_posts(
        offset: int = 0,
        limit: int = 20,
        db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Post).offset(offset).limit(limit))
    sources = result.scalars().all()
    return sources


@router.get('/sources/{source_id}', response_model=SourceResponse)
async def get_source(
        source_id: str,
        db: AsyncSession = Depends(get_db)
):
    source = await db.get(Source, source_id)
    if not source:
        raise HTTPException(HTTP_404_NOT_FOUND, 'Источник с данным id не найден')
    return source


@router.post('/sources/', status_code=201, response_model=SourceResponse)
async def create_resource(
        source_data: SourceCreate,
        db: AsyncSession = Depends(get_db)
):
    source = Source(**source_data.model_dump())
    db.add(source)
    await db.commit()
    await db.refresh(source)
    return source


@router.put('/sources/', response_model=SourceResponse)
async def update_source(
        source_id: str,
        source_data: SourceUpdate,
        db: AsyncSession = Depends(get_db)
):
    source = await db.get(Source, source_id)
    if not source:
        raise HTTPException(HTTP_404_NOT_FOUND, 'Источник с данным id не найден')

    source_data = source_data.model_dump(exclude_unset=True)
    for key, value in source_data.items():
        setattr(source, key, value)

    db.add(source)
    await db.commit()
    await db.refresh(source)
    return source


@router.delete('/sources/', status_code=HTTP_204_NO_CONTENT)
async def delete_source(
        source_id: str,
        db: AsyncSession = Depends(get_db)
):
    source = await db.get(Source, source_id)
    if not source:
        raise HTTPException(HTTP_404_NOT_FOUND, 'Источник с данным id не найден')
    await db.delete(source)
    await db.commit()


@router.get('/posts/', response_model=List[PostResponse])
async def get_posts(
        offset: int = 0,
        limit: int = 20,
        db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Post).offset(offset).limit(limit))
    sources = result.scalars().all()
    return sources


@router.get('/posts/{post_id}', response_model=PostResponse)
async def get_post(
        post_id: str,
        db: AsyncSession = Depends(get_db)
):
    post = await db.get(Post, post_id)
    if not post:
        raise HTTPException(HTTP_404_NOT_FOUND, 'Пост с данным id не найден')
    return post


# TODO: CRUD for keywords
# TODO: list and retrieve for news