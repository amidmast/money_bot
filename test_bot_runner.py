#!/usr/bin/env python3
"""
Test bot runner for automated testing of group vs personal data separation
"""

import asyncio
import logging
from telegram import Bot, Update
from telegram.ext import Application, ContextTypes
from telegram.error import TelegramError
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TestBotRunner:
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not self.bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN not found in environment")
        
        self.bot = Bot(token=self.bot_token)
        self.application = Application.builder().token(self.bot_token).build()
        
        # Test data
        self.personal_chat_id = None  # Will be set when we get the first message
        self.group_chat_id = None     # Will be set when we find a group
        
    async def find_chats(self):
        """Find available chats for testing"""
        try:
            # Get bot info
            bot_info = await self.bot.get_me()
            logger.info(f"Test bot info: {bot_info.username}")
            
            # Get updates to find chats
            updates = await self.bot.get_updates(limit=10)
            
            for update in updates:
                if update.message:
                    chat = update.message.chat
                    if chat.type == 'private':
                        self.personal_chat_id = chat.id
                        logger.info(f"Found personal chat: {chat.id}")
                    elif chat.type in ['group', 'supergroup']:
                        self.group_chat_id = chat.id
                        logger.info(f"Found group chat: {chat.id} - {chat.title}")
            
            return self.personal_chat_id is not None and self.group_chat_id is not None
            
        except Exception as e:
            logger.error(f"Error finding chats: {e}")
            return False
    
    async def send_test_commands(self):
        """Send test commands to both personal and group chats"""
        if not self.personal_chat_id or not self.group_chat_id:
            logger.error("Missing chat IDs")
            return
        
        try:
            # Test 1: Send /start to personal chat
            logger.info("=== TEST 1: Personal chat /start ===")
            await self.bot.send_message(
                chat_id=self.personal_chat_id,
                text="/start"
            )
            await asyncio.sleep(2)
            
            # Test 2: Send /start to group chat
            logger.info("=== TEST 2: Group chat /start ===")
            await self.bot.send_message(
                chat_id=self.group_chat_id,
                text="/start"
            )
            await asyncio.sleep(2)
            
            # Test 3: Add personal transaction
            logger.info("=== TEST 3: Add personal transaction ===")
            await self.bot.send_message(
                chat_id=self.personal_chat_id,
                text="Adding personal transaction: 100 USD for Food"
            )
            await asyncio.sleep(2)
            
            # Test 4: Add group transaction
            logger.info("=== TEST 4: Add group transaction ===")
            await self.bot.send_message(
                chat_id=self.group_chat_id,
                text="Adding group transaction: 200 USD for Group Food"
            )
            await asyncio.sleep(2)
            
            # Test 5: Check personal balance
            logger.info("=== TEST 5: Check personal balance ===")
            await self.bot.send_message(
                chat_id=self.personal_chat_id,
                text="/balance"
            )
            await asyncio.sleep(2)
            
            # Test 6: Check group balance
            logger.info("=== TEST 6: Check group balance ===")
            await self.bot.send_message(
                chat_id=self.group_chat_id,
                text="Checking group balance"
            )
            await asyncio.sleep(2)
            
            logger.info("=== All tests completed ===")
            
        except Exception as e:
            logger.error(f"Error sending test commands: {e}")
    
    async def monitor_responses(self, duration=30):
        """Monitor bot responses for the specified duration"""
        logger.info(f"Monitoring responses for {duration} seconds...")
        
        start_time = asyncio.get_event_loop().time()
        
        while (asyncio.get_event_loop().time() - start_time) < duration:
            try:
                updates = await self.bot.get_updates(limit=5)
                
                for update in updates:
                    if update.message:
                        chat = update.message.chat
                        chat_type = "PERSONAL" if chat.type == 'private' else f"GROUP ({chat.title})"
                        logger.info(f"RESPONSE [{chat_type}]: {update.message.text}")
                
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error monitoring responses: {e}")
                await asyncio.sleep(1)
    
    async def run_full_test(self):
        """Run the complete test suite"""
        logger.info("Starting automated test bot...")
        
        # Step 1: Find available chats
        if not await self.find_chats():
            logger.error("Could not find required chats for testing")
            return
        
        logger.info(f"Personal chat ID: {self.personal_chat_id}")
        logger.info(f"Group chat ID: {self.group_chat_id}")
        
        # Step 2: Send test commands
        await self.send_test_commands()
        
        # Step 3: Monitor responses
        await self.monitor_responses(duration=60)
        
        logger.info("Test completed!")

async def main():
    """Main function"""
    try:
        test_runner = TestBotRunner()
        await test_runner.run_full_test()
    except Exception as e:
        logger.error(f"Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
