from aiogram import Bot, Router, types
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from app.services.user_service import add_user_to_database, get_user_status, update_user_status
from aiogram import types
from app.database.engine import SessionLocal
from app.states import RegistrationStates
from app.models.user import User
from app.utils.debug import logger
from aiogram import types

from app.states import CommonStates

# async def handle_user_messages(message: types.Message, state: FSMContext):
#     user_data = await state.get_data()
#     message_count = user_data.get('message_count', 0)
#     message_count += 1
#
#     # TODO: Save the message to the database here
#
#     if message_count < 10:
#         await message.answer(f"Thanks, please send the {10 - message_count} remaining messages.")
#         await state.update_data(message_count=message_count)
#     else:
#         await message.answer("Thank you for sending 10 messages. You are now registered.")
#         # TODO: Update the user's registration status in the database here
#         await state.clear()



# # Registration command handler
#
# # TODO: Maybe move somewhere else
# async def cmd_register_start(message: types.Message, state: FSMContext):
#     user_id = message.from_user.id
#     username = message.from_user.username
#     session = SessionLocal()
#
#     try:
#         existing_user = session.query(User).filter_by(id=user_id).first()
#         if existing_user:
#             if not existing_user.is_active:
#                 # User exists but is not active, initiate the registration process
#                 await state.set_state(RegistrationStates.receiving_messages)
#                 await state.update_data(message_count=0)
#                 await message.answer(
#                     "You have been re-registered. Please send 10 messages to complete your registration.")
#                 await state.set_state(CommonStates.default)
#
#             else:
#                 # User is already active, no need to change state
#                 await message.answer("You are already registered.")
#         else:
#             # Create a new user instance, but don't set is_active to True yet
#             new_user = User(id=user_id, username=username, is_active=False)
#             session.add(new_user)
#             session.commit()
#             await state.set_state(RegistrationStates.receiving_messages)
#             await state.update_data(message_count=0)
#             await message.answer("You have been registered. Please send 10 messages to complete your registration.")
#     except Exception as e:
#         session.rollback()
#         await state.set_state(CommonStates.default)
#         await message.answer("Registration failed.")
#         logger.critical(str(e))  # Log the exception or handle it as necessary
#     finally:
#         session.close()


# async def handle_receiving_messages_on_registration(message: types.Message, state: FSMContext):
#     user_data = await state.get_data()
#     message_count = user_data.get('message_count', 0) + 1
#     await state.update_data(message_count=message_count)
#
#     if message_count < 10:
#         await message.answer(f"Message {message_count} received. {10 - message_count} messages left.")
#     else:
#         user_id = message.from_user.id
#         session = SessionLocal()
#         try:
#             existing_user = session.query(User).filter_by(id=user_id).first()
#             if existing_user and not existing_user.is_active:
#                 existing_user.is_active = True
#                 session.commit()
#                 await message.answer("Congratulations, your registration is now complete!")
#                 # Set the state to default after successful registration
#                 await state.set_state(CommonStates.default)
#             else:
#                 await message.answer("Unexpected error during registration completion. Please contact support.")
#         except Exception as e:
#             session.rollback()
#             await message.answer("Failed to complete registration.")
#             logger.critical(str(e))  # Log the exception
#         finally:
#             session.close()
#             await state.set_state(CommonStates.default)





async def cmd_start(message: types.Message, state: FSMContext):
    await state.set_state(CommonStates.default)
    await message.answer("Welcome! Use /register to sign up and /start_chatting to begin chatting with someone.")


async def message_reaction_handler(message_reaction: types.MessageReactionUpdated):
    # TODO: store all the messages sent by bot in DB, check whether this message is in DB to determine the sender: user or bot
    try:
        logger.debug("Emoji: ", message_reaction.new_reaction[0].emoji)
    except:
        logger.debug("Emoji: ", message_reaction.new_reaction.emoji)
