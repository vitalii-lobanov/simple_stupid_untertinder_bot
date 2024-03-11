
from aiogram.fsm.context import FSMContext
from database.engine import SessionLocal
from states import RegistrationStates
from models.user import User
from aiogram import types
from states import CommonStates
from utils.debug import logger
from models import ProfileDataTieredMessage

# This function will create a new user instance in the database and initiate the message receiving state.
async def create_new_registration(message: types.Message, state: FSMContext, user_id: int, username: str):
    session = SessionLocal()
    new_user = User(id=user_id, username=username, is_active=False)
    session.add(new_user)
    session.commit()
    await ask_user_to_send_messages_to_fill_profile(message, state)


# This function will handle any exceptions that occur during the registration process.
async def registration_failed(message: types.Message, state: FSMContext, exception: Exception):
    await state.set_state(CommonStates.default)
    await message.answer("Registration failed.")
    logger.critical(str(exception))


async def increment_message_count(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    message_count = user_data.get('message_count', 0) + 1
    await state.update_data(message_count=message_count)
    return message_count


async def check_message_threshold(message: types.Message, state: FSMContext, message_count: int):
    if message_count < 10:
        await message.answer(f"Message {message_count} received. {10 - message_count} messages left.")
    else:
        await complete_registration(message, state)


async def complete_registration(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    session = SessionLocal()
    try:
        existing_user = session.query(User).filter_by(id=user_id).first()
        if existing_user and not existing_user.is_active:
            existing_user.is_active = True
            session.commit()
            await message.answer("Congratulations, your registration is now complete!")
        else:
            await message.answer("Unexpected error during registration completion. Please contact support.")
    except Exception as e:
        await handle_registration_error(message, state, e)
    finally:
        session.close()
        await state.set_state(CommonStates.default)


async def handle_registration_error(message: types.Message, state: FSMContext, exception: Exception):
    session = SessionLocal()
    session.rollback()
    await message.answer("Failed to complete registration.")
    logger.critical(str(exception))  # Log the exception
    await state.set_state(CommonStates.default)
    session.close()


# This function will set the FSM state to RegistrationStates.receiving_messages to start receiving messages from the user.
async def ask_user_to_send_messages_to_fill_profile(message: types.Message, state: FSMContext):
    await state.set_state(RegistrationStates.receiving_messages)
    await state.update_data(message_count=0)
    logger.debug(f"User {message.from_user.id} has started registration.")
    await message.answer("Please send 10 messages to complete your registration.")


async def receiving_messages_on_registration_handler(message: types.Message, state: FSMContext):
    message_count = await increment_message_count(message, state)
    await save_registration_message(message, message_count)
    await check_message_threshold(message, state, message_count)




# async def save_registration_message(message: types.Message, message_count: int):
#     user_id = message.from_user.id
#     session = SessionLocal()
#     tier = message_count - 1
#     try:
#         new_message = ProfileDataTieredMessage(
#             user_id=user_id,
#             tier = tier,    
#             text=message.text or None,
#             audio=message.audio or None,
#             video=message.video or None,            
#             document=message.document or None,            
#             animation=message.animation or None,
#             author_signature=message.author_signature or None,
#             caption=message.caption or None,
#             caption_entities=message.caption_entities or None,
#             contact=message.contact or None,
#             forward_date=message.forward_date or None,
#             from_user= str(message.from_user).encode() or None,
#             game=message.game or None,
#             dice=message.dice or None,
#             entities=message.entities or None,
#             html_text=message.html_text or None,
#             invoice=message.invoice or None,
#             location=message.location or None,
#             link_preview_options=message.link_preview_options or None,
#             md_text=message.md_text or None,
#             media_group_id=message.media_group_id or None,
#             photo=message.photo or None,
#             poll=message.poll or None,
#             quote=message.quote or None,
#             sticker=message.sticker or None,
#             story=message.story or None,
#             voice=message.voice or None,
#             video_note=message.video_note or None
#         )
#         session.add(new_message)
#         session.commit()
#     except Exception as e:
#         session.rollback()
#         logger.critical(f"Failed to save message: {e}")
#     finally:
#         session.close()


# async def save_registration_message(message: types.Message, message_count: int):
#     user_id = message.from_user.id
#     session = SessionLocal()
#     tier = message_count - 1
#     photo = None
#     video = None

#     # Extract the file ID of the largest photo
#     if message.photo:
#         photo = message.photo[-1].file_id  # Get the file_id of the last (largest) photo size

#     # Extract the file ID of the video
#     if message.video:
#         video = message.video.file_id

#     try:
#         new_message = ProfileDataTieredMessage(
#             user_id=user_id,
#             tier=tier,
#             text=message.text or None,
#             audio=message.audio.file_id if message.audio else None,
#             video=video,            
#             document=message.document.file_id if message.document else None,
#             animation=message.animation or None,
#             author_signature=message.author_signature or None,
#             caption=message.caption or None,
#             caption_entities=message.caption_entities or None,
#             contact=message.contact or None,
#             forward_date=message.forward_date or None,
#             from_user= str(message.from_user).encode() or None,
#             game=message.game or None,
#             dice=message.dice or None,
#             entities=message.entities or None,
#             html_text=message.html_text or None,
#             invoice=message.invoice or None,
#             location=message.location or None,
#             link_preview_options=message.link_preview_options or None,
#             md_text=message.md_text or None,
#             media_group_id=message.media_group_id or None,
#             photo=photo,
#             poll=message.poll or None,
#             quote=message.quote or None,
#             sticker=message.sticker or None,
#             story=message.story or None,
#             voice=message.voice or None,
#             video_note=message.video_note or None

#         )
#         session.add(new_message)
#         session.commit()
#     except Exception as e:
#         session.rollback()
#         logger.critical(f"Failed to save message: {e}")
#     finally:
#         session.close()


async def save_registration_message(message: types.Message, message_count: int):
    user_id = message.from_user.id
    session = SessionLocal()
    tier = message_count - 1
    photo = None
    video = None

    # Extract the file ID of the largest photo
    if message.photo:
        photo = message.photo[-1].file_id  # Get the file_id of the last (largest) photo size

    try:
        new_message = ProfileDataTieredMessage(
            user_id=user_id,
            tier=tier,
            text=message.text or None,
            audio=message.audio.file_id.encode("utf-8") if message.audio else None,
            video= message.video.file_id.encode("utf-8") if message.video else None, 
            document=message.document.file_id.encode("utf-8") if message.document else None,
            animation=message.animation.file_id.encode("utf-8") if message.animation else None,
            author_signature=message.author_signature if message.author_signature else None,
            caption=message.caption if message.caption else None,
            caption_entities=message.caption_entities if message.caption_entities else None,
            contact=message.contact if message.contact else None,
            forward_date=message.forward_date if message.forward_date else None,
            from_user= str(message.from_user).encode() if message.from_user else None,
            game=message.game if message.game else None,
            dice=message.dice if message.dice else None,
            entities=message.entities if message.entities else None,
            html_text=message.html_text if  message.html_text else None,
            invoice=message.invoice if message.invoice else None,
            location=message.location if message.location else None,
            link_preview_options=message.link_preview_options if message.link_preview_options else None,
            md_text=message.md_text if message.md_text else None,
            media_group_id=message.media_group_id if message.media_group_id else None,

            photo=photo if photo else None, 
            poll=message.poll  if message.poll else None,
            quote=message.quote if message.quote else None,
            sticker=message.sticker if message.sticker else None,
            story=message.story if message.story else None,
            voice=message.voice if message.voice else None,
            video_note=message.video_note if message.video_note else None

        )
        session.add(new_message)
        session.commit()
    except Exception as e:
        session.rollback()
        logger.critical(f"Failed to save message: {e}")
    finally:
        session.close()


# This function will check if the user is already registered or not and initiate the registration process if necessary.
# async def start_registration_handler(message: types.Message, state: FSMContext):
#     user_id = message.from_user.id
#     session = SessionLocal()
#     try:
#         existing_user = session.query(User).filter_by(id=user_id).first()
#
#         if existing_user and not existing_user.is_active:
#             await ask_user_to_send_messages_to_fill_profile(message, state)
#         elif existing_user:
#             await message.answer("You are already registered.")
#         else:
#             await create_new_registration(message, state, user_id, message.from_user.username)
#     except Exception as e:
#         await registration_failed(message, state, e)
#     finally:
#         session.close()




async def start_registration_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    with SessionLocal() as session:
        try:
            existing_user = session.query(User).filter_by(id=user_id).first()
            # Check if user is already registered
            if existing_user:
                # Check if the user has the required number of profile messages
                profile_messages_count = session.query(ProfileDataTieredMessage).filter_by(user_id=user_id).count()

                if existing_user.is_active and profile_messages_count == 10:
                    # Notify the active user with the complete profile that their existing messages will be used
                    await message.answer(
                        "You have already created a profile and your existing messages will be used. "
                        "If you want to create a new profile, please use /hard_unregister command."
                    )
                elif not existing_user.is_active:
                    # Handle reactivation or continuation of registration for inactive users
                    # await ask_user_to_send_messages_to_fill_profile(message, state)
                    # Or reactivate the user and notify them accordingly
                    existing_user.is_active = True
                    session.commit()
                    await message.answer("Your profile has been reactivated.")
                else:
                    # The user is active but doesn't have 10 messages, proceed with message collection
                    await ask_user_to_send_messages_to_fill_profile(message, state)
            else:
                # User is not registered, start new registration
                await create_new_registration(message, state, user_id, message.from_user.username)

        except Exception as e:
            await registration_failed(message, state, e)
        finally:
            session.close()
