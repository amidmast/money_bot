#!/usr/bin/env python3
"""
Test script to verify data separation between personal and group chats
"""

import asyncio
import logging
from telegram import Bot
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

class DataSeparationTester:
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not self.bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN not found in environment")
        
        self.bot = Bot(token=self.bot_token)
        
        # These should be set to your actual chat IDs
        self.personal_chat_id = 500048632  # Your personal chat ID
        self.group_chat_id = -4843883018   # Your group chat ID
        
    async def send_test_sequence(self):
        """Send a sequence of test commands"""
        logger.info("=== STARTING DATA SEPARATION TEST ===")
        
        try:
            # Test 1: Clear any existing context by sending /start to personal
            logger.info("TEST 1: Sending /start to personal chat")
            await self.bot.send_message(
                chat_id=self.personal_chat_id,
                text="/start"
            )
            await asyncio.sleep(3)
            
            # Test 2: Send /start to group
            logger.info("TEST 2: Sending /start to group chat")
            await self.bot.send_message(
                chat_id=self.group_chat_id,
                text="/start"
            )
            await asyncio.sleep(3)
            
            # Test 3: Try to add personal transaction
            logger.info("TEST 3: Attempting to add personal transaction")
            await self.bot.send_message(
                chat_id=self.personal_chat_id,
                text="Let's add a personal transaction"
            )
            await asyncio.sleep(2)
            
            # Test 4: Try to add group transaction
            logger.info("TEST 4: Attempting to add group transaction")
            await self.bot.send_message(
                chat_id=self.group_chat_id,
                text="Let's add a group transaction"
            )
            await asyncio.sleep(2)
            
            # Test 5: Check personal balance
            logger.info("TEST 5: Checking personal balance")
            await self.bot.send_message(
                chat_id=self.personal_chat_id,
                text="/balance"
            )
            await asyncio.sleep(3)
            
            # Test 6: Check group balance
            logger.info("TEST 6: Checking group balance")
            await self.bot.send_message(
                chat_id=self.group_chat_id,
                text="Let's check group balance"
            )
            await asyncio.sleep(3)
            
            logger.info("=== TEST SEQUENCE COMPLETED ===")
            logger.info("Please check the bot logs to see if data separation is working correctly")
            
        except Exception as e:
            logger.error(f"Error during test sequence: {e}")
    
    async def monitor_bot_logs(self, duration=30):
        """Monitor bot responses"""
        logger.info(f"Monitoring bot responses for {duration} seconds...")
        
        start_time = asyncio.get_event_loop().time()
        
        while (asyncio.get_event_loop().time() - start_time) < duration:
            try:
                updates = await self.bot.get_updates(limit=5)
                
                for update in updates:
                    if update.message:
                        chat = update.message.chat
                        chat_type = "PERSONAL" if chat.type == 'private' else f"GROUP ({chat.title})"
                        logger.info(f"BOT RESPONSE [{chat_type}]: {update.message.text}")
                
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"Error monitoring responses: {e}")
                await asyncio.sleep(2)

async def main():
    """Main function"""
    try:
        tester = DataSeparationTester()
        
        # Send test sequence
        await tester.send_test_sequence()
        
        # Monitor responses
        await tester.monitor_bot_logs(duration=60)
        
    except Exception as e:
        logger.error(f"Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
