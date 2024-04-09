from collections import deque
from aiogram import types
from aiogram.dispatcher.middlewares.base import BaseMiddleware

from typing import Dict, Deque
from utils.d_debug import d_logger



# A dictionary to hold queues for each user
message_queues: Dict[int, Deque[types.Message]] = {}

class MessageOrderingMiddleware(BaseMiddleware):
    def __init__(self, router):
        self.router = router
        super().__init__()

   
    async def __call__(self, handler, event, data):
        if isinstance(event, types.Message):
            user_id = event.from_user.id
            if user_id not in message_queues:
                message_queues[user_id] = deque()

            message_queues[user_id].append(event)
            if len(message_queues[user_id]) == 1:
                while message_queues[user_id]:
                    current_event = message_queues[user_id][0]  # Peek the first message
                    try:
                        d_logger.debug(f"Process message {current_event.message_id} with text {current_event.text}")
                        await handler(current_event, data)
                    except Exception as e:
                        d_logger.error(f"Error processing message: {e}")
                    finally:
                        # Remove the processed message from the queue
                        processed_event = message_queues[user_id].popleft()
                        d_logger.debug(f"Remove message {processed_event.message_id} with text {processed_event.text} from the queue")
            else:
                    # If there's already a message being processed, delay further processing
                d_logger.debug(f"Skip message {event.message_id} with text: {event.text}. We will process it later from the queue.")




# # The simpliest message ordering middleware
# # A dictionary to hold queues for each user
# message_queues: Dict[int, Deque[types.Message]] = {}

# class MessageOrderingMiddleware(BaseMiddleware):
#     def __init__(self, router):
#         self.router = router
#         super().__init__()

#     async def __call__(self, handler, event, data):
#         if isinstance(event, types.Message):
#             user_id = event.from_user.id
#             if user_id not in message_queues:
#                 message_queues[user_id] = deque()

#             message_queues[user_id].append(event)
#             if len(message_queues[user_id]) == 1:
#                 # If this is the only message in the queue, process it
#                 while message_queues[user_id]:
#                     current_event = message_queues[user_id][0]  # Peek the first message
#                     try:
#                         d_logger.debug(f"Process message {event.message_id} with text {current_event.text}")
#                         await handler(current_event, data)
#                     finally:
#                         # Remove the processed message from the queue
#                         d_logger.debug(f"Remove message {event.message_id} with text {event.text} from the queue")
#                         message_queues[user_id].popleft()
#             else:
#                 # If there's already a message being processed, delay further processing
#                 d_logger.debug(f"Skip message {event.message_id} with text: {event.text}. We will process it later from the queue.")

