from fastapi import APIRouter
from app.models import User

router = APIRouter()
users = []

@router.post('/users')
def create_user(user: User):
    users.append(user)
    return user

@router.get('/users')
def list_users():
    return users