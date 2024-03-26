# TODO: wrap all the user messages as functions


def message_you_now_connected_to_the_conversation_partner() -> str:
    return "You are now connected with a chat partner!"


def message_a_conversation_partner_found() -> str:
    return "Someone became your chat partner!"


def message_this_is_bot_message() -> str:
    return "<b>THIS IS BOT'S SERVICE MESSAGE! IT WAS NOT FORWARDED FROM YOUR CHAT PARTNER OR ANY OTHER HUMAN. IT WAS GENERATED BY THE BOT.</b>\n\n"


def message_the_last_tier_reached() -> str:
    return "You have reached the last score threshold. You can continue chat with the current partner or use /next_please command to try again."


def message_you_are_not_in_chatting_state() -> str:
    return "You are not currently in a conversation. You can use '/start_chatting' to start one."


def message_you_send_end_command_and_your_partner_has_sent_it_earlier() -> str:
    return "You sent '/next_please' command. Your partner has sent it earlier. Conversation ended."


def message_you_sent_end_command_earlier_and_your_just_sent_it_now() -> str:
    return "You sent '/next_please' command earlier. Your partner just sent it now. Conversation ended."


def message_you_sent_end_command_earlier_and_timer_expired() -> str:
    return "You sent '/next_please' command earlier. The timer expired. Conversation ended."


def message_your_partner_sent_end_command_earlier_and_timer_expired() -> str:
    return "Your partner sent '/next_please' command earlier. The timer expired. Conversation ended."


def message_this_message_is_forwarded(
    original_sender_username: str, message_text: str
) -> str:
    return f"FORWARDED FROM @{original_sender_username}\n\n{message_text}"


def message_user_has_been_unregistered() -> str:
    return "You have been unregistered. Your profile is present in database. You can use '/register' command to start again."


def message_cannot_unregister_not_registered_user() -> str:
    return "You cannot unregister not registered user. You can use '/register' command to start again."


def message_user_has_already_been_hardly_unregistered() -> str:
    return "You have already unregistered. Your profile was removed from database. You can use '/register' command to start again."


def message_reactivation_user_profile_completed() -> str:
    return "Your old profile has been reactivated. Your old messages will be used."


def message_non_registered_users_cannot_start_chatting() -> str:
    return "Non-registered users cannot start chatting. You can use '/register' command to start again."


def message_you_now_ready_to_chat_please_wait_the_partner_to_connect() -> str:
    return "You are now ready to chat. Please wait for your partner to connect."


# def message_you_are_not_in_default_state_and_cannot_renew_profile():
#     return "You are not in default state. Stop all the conversations and other activities and use '/renew_profile' command to start again."


def message_you_cannot_unregister_now() -> str:
    return "You cannot unregister now. Finish all the conversations and other activities and use '/register' command to start again."


def message_you_have_been_registered_successfully() -> str:
    return "You have been registered successfully. You can use '/start_chatting' command to start chatting with someone."


def message_now_please_send_profile_messages(messages_count: int = -1) -> str:
    if messages_count == -1:
        raise ValueError("messages_count cannot be -1.")
    else:
        return f"Please send {messages_count} profile messages."


def message_cmd_start_welcome_message() -> str:
    return "Welcome! Use /register to sign up and /start_chatting to begin chatting with someone."


def message_registration_failed() -> str:
    return "Registration failed. Please contact support."


def message_profile_message_received_please_send_the_remaining(
    message_count: int = -1, total_messages_count: int = -1
) -> str:
    if message_count == -1 or total_messages_count == -1:
        raise ValueError("message_count and total_messages_count cannot be -1.")
    else:
        return f"Message {message_count} received. {total_messages_count - message_count} messages left."


def message_no_partners_ready_to_chat_available_we_will_inform_you_later() -> str:
    return "No partners are ready to chat. We will inform you later."


def message_you_should_not_react_your_own_messages() -> str:
    return "You should not react your own messages."


def message_you_have_reached_the_next_tier(
    current_score: int = 0, reached_tier: int = 0
) -> str:
    return f"Your score is {current_score}. You have reached the {reached_tier} score threshold."


def message_you_are_not_in_default_state_and_cannot_register() -> str:
    return "You are not in default state. Stop all the conversations and other activities and use '/register' command to try again."
