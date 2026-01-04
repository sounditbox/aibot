import logging
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.exceptions import HTTPException
from starlette.status import HTTP_404_NOT_FOUND, HTTP_204_NO_CONTENT

from app.api.schemas import (
    SourceResponse, 
    SourceCreate, 
    SourceUpdate, 
    PostResponse,
    TelegramAuthRequest,
    TelegramAuthResponse
)
from app.database import get_db, Source, Post
from app.tasks import publish_posts_task, parse_news
from app.telegram.bot import authorize_telegram, get_telegram_client

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


@router.put('/sources/{source_id}', response_model=SourceResponse)
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

    await db.commit()
    await db.refresh(source)
    return source


@router.delete('/sources/{source_id}', status_code=HTTP_204_NO_CONTENT)
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
    posts = result.scalars().all()
    return posts


@router.get('/posts/{post_id}', response_model=PostResponse)
async def get_post(
        post_id: str,
        db: AsyncSession = Depends(get_db)
):
    post = await db.get(Post, post_id)
    if not post:
        raise HTTPException(HTTP_404_NOT_FOUND, 'Пост с данным id не найден')
    return post


@router.post('/publish-posts/', status_code=200)
async def publish_posts():
    publish_posts_task.delay()
    return {'status': 'started'}


@router.post('/parse-sources/', status_code=200)
async def parse_sources():
    parse_news.delay()
    return {'status': 'started'}


@router.post('/telegram/authorize/', response_model=TelegramAuthResponse)
async def authorize_telegram_endpoint(request: TelegramAuthRequest):
    """
    Процесс авторизации:
    1. Первый запрос: отправьте только phone - получите код в Telegram
    2. Второй запрос: отправьте phone и code - авторизуетесь
    3. Если требуется 2FA: отправьте phone, code и password
    """
    result = await authorize_telegram(
        phone=request.phone,
        code=request.code,
        password=request.password
    )
    return TelegramAuthResponse(**result)


@router.get('/telegram/status/')
async def get_telegram_status():
    from telethon import TelegramClient
    from app.config import settings
    
    if not settings.TELERGAM_API_ID or not settings.TELERGAM_API_HASH:
        return {
            'authorized': False,
            'message': 'Telegram credentials not configured'
        }
    
    client = TelegramClient(
        settings.TELERGAM_SESSION_NAME,
        settings.TELERGAM_API_ID,
        settings.TELERGAM_API_HASH
    )
    
    try:
        await client.connect()
        
        if await client.is_user_authorized():
            me = await client.get_me()
            return {
                'authorized': True,
                'phone': me.phone,
                'username': me.username,
                'first_name': me.first_name,
                'last_name': me.last_name
            }
        else:
            return {
                'authorized': False,
                'message': 'Telegram client not authorized'
            }
    except Exception as e:
        return {
            'authorized': False,
            'message': f'Error checking status: {str(e)}'
        }
    finally:
        await client.disconnect()

# TODO: CRUD for keywords
# TODO: list and retrieve for news