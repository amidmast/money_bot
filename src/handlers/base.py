from abc import ABC, abstractmethod
from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session
from src.database.session import get_session

class BaseHandler(ABC):
    def __init__(self):
        self.db: Session = get_session()
    
    def __del__(self):
        if hasattr(self, 'db'):
            self.db.close()
    
    @abstractmethod
    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        pass
    
    def get_user_from_update(self, update: Update):
        """Extract user information from Telegram update"""
        user = update.effective_user
        return {
            'telegram_id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'language_code': user.language_code
        }
    
    def get_context_from_update(self, update: Update):
        """Get the correct context (user or group) from Telegram update"""
        chat = update.effective_chat
        
        # Determine if this is a group or personal chat
        is_group = chat.type in ['group', 'supergroup', 'channel']
        
        if is_group:
            # For groups, return group data
            return {
                'telegram_id': chat.id,  # Group's telegram ID (negative)
                'is_group': True,
                'group_title': chat.title,
                'group_type': chat.type,
                'first_name': chat.title,
                'username': None,
                'last_name': None,
                'language_code': 'en'  # Default for groups
            }
        else:
            # For personal chats, return user data
            user = update.effective_user
            return {
                'telegram_id': user.id,
                'is_group': False,
                'group_title': None,
                'group_type': None,
                'first_name': user.first_name,
                'username': user.username,
                'last_name': user.last_name,
                'language_code': user.language_code
            }