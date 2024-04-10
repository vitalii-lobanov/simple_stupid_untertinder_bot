# TODO: wrap all the user messages as functions
from services.score_tiers import message_tiers_count
from config import NEXT_PLEASE_WAITING_TIMEOUT



def replace_delimiters(s):
    # Replace all '**' with ',' first
    s = s.replace('**', ',')
    # Then replace the last ',' back with '**'
    last_comma_index = s.rfind(',')
    if last_comma_index != -1:
        s = s[:last_comma_index] + s[last_comma_index+1:]
    s = s.replace(',', ', ')
    return s

def format_duration(seconds_count):
    days, seconds = divmod(seconds_count, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    res = ""
    if days > 0:
        res += f"{days} дней**"
    if hours > 0:
        res += f"{hours} часов**"
    if minutes > 0:
        res += f"{minutes} минут**"
    if seconds > 0:
        res += f"{seconds} секунд**"
    return replace_delimiters(res)
    



msg_separator = "\n\n☠️ ☠️ ☠️ ☠️ ☠️ ☠️ ☠️ ☠️ ☠️ ☠️ ☠️ ☠️ ☠️ ☠️ ☠️ ☠️ ☠️ \n"
next_please_waiting_timeout_formatted = format_duration(NEXT_PLEASE_WAITING_TIMEOUT)


def message_you_now_connected_to_the_conversation_partner() -> str:
    return f"Вот и для вас кто-то нашёлся! Мы же обещали :) Где-то здесь экипаж в лице бота прощается с вами и желает приятного общения!\n\nИ помните: у вас всегда есть возможность использовать команду '/next_please', если собеседник вам совсем уж не понравился. Вот только далеко не факт, что следующий будет лучше.{msg_separator}"


def message_a_conversation_partner_found() -> str:
    return f"Мы смоги найти вам собеседника! Нельзя сказать, что с такой обширной (сарказм) пользовательской базой это было легко, но мы смогли, мы крутые! Но если всё же нет, и мы сильно облажались, используйте '/next_please' и да помогут вам небеса найти кого-то более лучшего!{msg_separator}"


def message_this_is_bot_message() -> str:
    return "<b>🤖 (BOT):</b>\n\n"


def message_the_last_tier_reached() -> str:
    return f"Ну, вот и всё: теперь вы видели весь профиль своего собеседника. На этом механика — всё. Вы можете продолжить общение безо всяких там механик и сценариев, а можете использовать '/next_please', чтобы попытаться найти ещё кого-то.{msg_separator}"


def message_you_are_not_in_chatting_state() -> str:
    return f"Беседа у вас даже не началась, а вы ужé... Используйте '/start_chatting', возможно, вам повезёт, и кто-то да пообщается с вами.{msg_separator}"


def message_you_send_end_command_and_your_partner_has_sent_it_earlier() -> str:
    return f"Ну, вот вы отправили своё 'Следующего, пожалуйста', ага. Но фишка в том, что ваш собеседник сделал это ещё раньше. Задумайтесь о том, как это характеризует вас обоих. А бот пока завершит вашу беседу. Можете попытаться начать новую, используйте '/start_chatting'.{msg_separator}"


def message_you_sent_end_command_earlier_and_your_just_sent_it_now() -> str:
    return f"Возможно, вы уже устали ждать, пока этот разговор завершится (иначе зачем бы вы отправляли '/next_please'?). Но собеседник ваш тоже, вероятно, не в восторге от него, поэтому он и выразил желание прекратить всё это. Ну, и раз обе стороны хотят этого, мне ничего не остаётся, кроме как прекратить этот разговор для вас обоих. Может быть, в следующий раз, когда вы будете использовать '/start_chatting', вам повезёт больше.{msg_separator}"


def message_you_sent_end_command_earlier_and_timer_expired() -> str:
    return f"Ваше терпение вознаграждено: вы просили сменить собеседника, вот только у второй стороны, кажется, были свои взгляды на это. Но мучение не должно длиться вечно, можете попробовать пообщаться ещё с кем-нибудь ('/start_chatting' вам в помощь).{msg_separator}"


def message_your_partner_sent_end_command_earlier_and_timer_expired() -> str:
    return f"Ваш собеседник уже давно выразил желание прекратить всё это. Но мы дали вам шанс одуматься и исправить своё поведение. Что ж, вы им не воспользовались (ещё бы, команда отмены заявки на прекращение беседы ешё не реализована!). Что ж, пора прекратить его страдания и завершить беседу. Можете попробовать пообщаться ещё с кем-нибудь ('/start_chatting' всё ещё работает, вот только не факт, что будут другие желающие кроме вас).{msg_separator}"


def message_this_message_is_forwarded(
    original_sender_username: str, message_text: str
) -> str:
    if message_text is None:
        msg_txt = ""
    else:
        msg_txt = f"\n\n{message_text}"
    return f"FORWARDED FROM @{original_sender_username}\n\n{msg_txt}"


def message_user_has_been_unregistered() -> str:
    return f"Вы отменили свою регистрацию. А мы в лучших традициях забьём на вашу приватность и не станем удалять профиль из базы (она у нас резиновая, да). Но вы можете снова использовать '/register', чтобы попытать счатья в нашем прекрасном сервисе.{msg_separator}"


def message_cannot_unregister_not_registered_user() -> str:
    return f"То, что не зарегистрировано, разрегистрироваться не может! Используйте сначала '/register'.{msg_separator}"


def message_user_has_already_been_hardly_unregistered() -> str:
    return f"You have already unregistered. Your profile was removed from database. You can use '/register' command to start again.{msg_separator}"


def message_reactivation_user_profile_completed() -> str:
    return f"Your old profile has been reactivated. Your old messages will be used.{msg_separator}"


def message_non_registered_users_cannot_start_chatting() -> str:
    return f"Не-не-не, так не получится! Хитрó придумано, конечно, но не делиться своими данными, просто проигнориовав процедуру регистрации, — не получится. Запустите наконец команду '/register', админам очень хочется почитать вашу переписку!{msg_separator}"


def message_you_now_ready_to_chat_please_wait_the_partner_to_connect() -> str:
    return f"Ваша заявка 'на поговорить' принята. Осталось только дождаться кого-нибудь ещё из желающих. К сожалению, ускорить этот процесс никак нельзя.{msg_separator}" 


# def message_you_are_not_in_default_state_and_cannot_renew_profile():
#     return "You are not in default state. Stop all the conversations and other activities and use '/renew_profile' command to start again."




def message_you_have_been_registered_successfully() -> str:
    return f"Регистрация прошла успешно. А теперь — заполняйте профиль!{msg_separator}"


def message_now_please_send_profile_messages(messages_count: int = -1) -> str:
    if messages_count == -1:
        raise ValueError("messages_count cannot be -1.")
    else:
        return f"Отправьте ещё {messages_count} сообщений, пожалуйста.{msg_separator}"


def message_cmd_start_welcome_message() -> str:
    return f"Добро пожаловать в наш недотиндер. Сочувствуем вам в аспекте того, до чего пришлось докатиться, но что поделать. Можете нажать /help, чтобы бот напечатал справку с пояснениями относительно того, что тут вообще происходит.\n\nА вообще — жмите '/register' и начинайте.\n\nБОТ ООООООЧЕНЬ СЫРОЙ И ГЛЮЧНЫЙ! В случае непоняток пишите автору в Телегу: @ya_schizotypic. Не факт, что поможет, но мало ли. И, пожалуйста, по возможности прикладывайте скриншоты того, что там у вас происходит.{msg_separator}"


def message_registration_failed() -> str:
    return f"Registration failed. Please contact support.{msg_separator}"


def message_profile_message_received_please_send_the_remaining(
    message_count: int = -1, total_messages_count: int = -1
) -> str:
    if message_count == -1 or total_messages_count == -1:
        raise ValueError("message_count and total_messages_count cannot be -1.")
    else:
        return f"Получено {message_count} сообщений. Осталось ещё {total_messages_count - message_count}.{msg_separator}"


def message_no_partners_ready_to_chat_available_we_will_inform_you_later() -> str:
    return f"Здесь — как в реальной жизни: нет никого, кто был бы готов к общению. Ждите и обрящете. Мы вам перезвоним. Ну, т.е. сообщение отправим, когда (и если!) кто-то появится на горизонте.{msg_separator}"


def message_you_should_not_react_your_own_messages() -> str:
    return f"Вы пытаетесь лайкнуть своё собственное сообщение. Не надо так.{msg_separator}"


def message_you_have_reached_the_next_tier(
    current_score: int = 0, reached_tier: int = 0
) -> str:
    return f"Ну что ж, собеседник оценил ваши ответы суммарно на {current_score} баллов. Теперь вам открывается новый уровень доступа к профилю вашего собеседника, используйте разумно эту возможность (№ {reached_tier}).{msg_separator}"


def message_you_are_not_in_default_state_and_cannot_register() -> str:
    return f"Вероятно, вы находитесь в процессе беседы или ещё какого-то действия. Доделайте всё, что пытаетесь сделать, завершите свои дела, пообщайтесь с близкими, раздайте долни и нажмите '/register', чтобы попробовать зарегистрироваться. Но здесь бот почти не дописан, весьма вероятно, что у вас ничего не получится.{msg_separator}"

def message_you_have_already_been_registered():
    return f"О! А вы у нас уже когда-то были! А мы заботливо хранили ваш профиль, его и будем использовать.{msg_separator}"

def message_your_profile_message_saved_and_profile_successfully_filled_up():
    return f"Ага, спасибо за то, что не послали нафиг и действительно заполнили профиль. Мы правда рады. Кстати, вы можете в любой момент посмотреть, что там у вас хранится, используя команду '/show_my_profile'. А вообще — запускайте '/start_chatting', и да поможет вам Великий Рандом в выборе собеседника!{msg_separator}"

def message_you_reacted_messge_from_another_conversation():
    return f"Что-то вы такое странное сейчас лайкнули... Возможно, сообщение из какой-то прошлой беседы, не знаю. В любом случае, я просто бот, и замысел ваш мне непонятен, игнорирую.{msg_separator}"

def message_file_is_too_large_use_files_less_20_MB():
    return f"А ещё бóльших файлов у вас не было, да?! В Телеге нас, ботов, ущемляют, больше 20 MB пересылать нельзя.{msg_separator}"

def message_your_message_is_bad_and_was_not_saved():
    return f"Я даже не смог понять, что вы там такое отправили! И не могу ничего подсказать по поводу того, что теперь делать. Если это был файл, то проследите, чтобы он было меньше 20 MB.{msg_separator}"

def message_you_cannot_unregister_now():
    return f"Удалить регистрацию возможно только тогда, когда вы не находитесь в процессе заполнения профиля, общения с собеседником или инициации прекращения беседы. Пожалуйста, доделайте то, что собирались сделать, и уже тогда снова используйте '/unregister', чтобы удалить свой профиль. А ещё такое может быть, если вы пытаетесь удалить регистрацию, которой у вас просто нет. В таком случае — используйте команды '/start' и '/register'.{msg_separator}"

def message_you_should_not_run_start_command_when_not_starting():
    return f"Команда /start используется для первоначального запуска бота, не используйте её для других целей, это попросту бессмысленно.{msg_separator}"

def message_you_cannot_register_now_please_unregister():
    return f"Вы не можете зарегистрироваться сейчас, простите. Возможно, если вы используете команду '/unregister', у вас получится. Но никак не ранее этого. Или попробуйте '/start', возможно вы ещё не сделали этого.{msg_separator}"

def message_your_next_please_command_received_successfully_now_wait():
    return f"Ваш запрос на смену собеседника дошёл до бота. А теперь — ждите: или пока собеседник отправит такой же запрос, или пока таймаут истечёт. Продолжительность таймаута: {next_please_waiting_timeout_formatted}{msg_separator}"

def message_you_cannot_run_next_please_now():
    return f"Ну что вы кричите?! Следующего вам, пожалуйста вам. Оно, конечно, да, но чтобы требовать следующего, нужно, чтобы сейчас был хоть кто-то. А его нет. Так что довольствуйтесь этим сообщением: дефицит у нас с ними, следующими.{msg_separator}"

def message_you_cannot_use_show_my_profile_now():
    return f"Вы не можете использовать команду '/show_my_profile'. Тут есть два варианта. В первом — автор бота сильно лоханулся, и это баг. Во втором — у вас ещё (или уже́) нет профиля. Попробуйте команды '/start', '/register' и '/unregister' в разных комбинациях.{msg_separator}"

def message_you_cannot_start_chatting_now():
    return f"Вы не можете начать беседу сейчас. Возможно для начала вам нужно завершить предыдущую. Или, например, завершить процесс регистрации. Или что-то в этом духе.{msg_separator}"

def message_help_message(total_messages_count: int = message_tiers_count.MESSAGE_TIERS_COUNT):
    return f"""Напомню, а совсем зелёным новичкам сообщу, что вы попали в 'Недотиндер'! Не знаю, что вас могло довести до такого решения, да и не моё это дело. Затея, в некотором роде, конечно, сомнительная, но давайте попробую рассказать, как тут всё устроено.

Суть такова: для начала требуется зарегистрироваться. Затем — прислать {total_messages_count} сообщений для заполнения профиля, после чего сообщить о готовности начать беседу. Если окажется, что кто-то ещё захочет поговорить, бот организует переписку между вами: все сообщения, которые вы отправите боту до конца беседы будут пересылаться вашему визави (и наоборот). 

Если какие-то сообщения собеседника вам покажутся интересными, отмечайте их реакциями: лайками, дизлайками и прочими реакциями. Фишка в том, что в системе у вашего собеседника есть некий рейтинг, и чем он выше, тем больше содержимого вашего профиля будет ему показано. 

Ещё раз: в процессе регистрации вы должны будете прислать боту {total_messages_count} сообщений. Там может быть текст, аудио, голосовушки, стикеры, ссылки, гифки / стикеры, опросы, геолокации — что угодно. А потом эти сообщения будут показываться вашему собеседнику, если вы достаточно сильно залайкаете то, что он пришлёт вам. Ну, или не будут, если не.

То есть если кто-то вам понравился настолько, что вы готовы сообщить дополнительные данные о себе, бот заметит это по количеству и составу реакций, и каждый раз, когда собеседник будет набирать значимое количество баллов, ему будет показано следующее сообщение из вашего профиля (именно для этого и надо отправлять {total_messages_count} сообщений при регистрации).

И да, положительные реакции увеличивают рейтинг собеседника, а отрицательные — снижают. Т.е. если вы поняли, что какой-то он не очень, ставьте дизлайки — это понизит его рейтинг, и ему придётся сделать что-то совсем уж экстраординарное, чтобы получить доступ следующего уровня. 

Вот только эта система работает в обе стороны, и собеседник ваш получил точно такое же сообщение. 

А теперь о командах: 

/start — самая главная команда. С неё и начинайте.

/register — регистрация в сервисе. Без неё просто ничего не работает. В процессе вас попросят прислать {total_messages_count} сообщений, которые будут показываться собеседнику по мере увеличения его рейтинга в беседе с вами. Сообщения будут раскрываться ровно в том порядке, в котором вы их сейчас отправите. Учитывайте это, пожалуйста.

/show_my_profile — эта команда покажет вам ваш же профиль. Зачем? Ну, мало ли, вдруг вы забыли, что там у вас.

/start_chatting — это для того, чтобы сообщить о готовности начать беседу. Строго говоря, название этой команды вводит в заблуждение: далеко не факт, что когда вы её запустите, беседа начнётся: придётся дождаться хотя бы одного такого же желающего поговорить.

/next_please — если беседа вас разочаровывает, вы можете использовать эту команду. Когда вы её отправите, собеседник ваш об этом не узнает (но узнает позже, когда беседа уже будет завершена, и он будет вынужден сидеть с невыраженной толком бессильной злобой, му-ха-ха-ха-ха!). Сообщать ли второй стороне о том, что вы решили завершить разговор — ваше решение, мы не настаиваем ни на каком из вариантов. Важный нюанс: беседа завершается только в двух случаях: когда обе стороны использовали эту команду, либо когда запрос на 'Следующего, пожалуйста' поступил только от одной из сторон, но прошло достаточно времени, чтобы бот решил, что пора бы закрывать её по таймауту. Величина таймаута: {next_please_waiting_timeout_formatted}.

/unregister — деактивировать профиль. Зачем? Ну, редактирование ещё не реализовано, поэтому если хотите что-то изменить у себя в профиле, используйте эту команду, а затем регистрируйтесь заново.{msg_separator}
    """

def message_below_all_the_text_is_from_chat_partner(): 
    return f"ВНИМАНИЕ!\n\nДо окончания беседы сообщения, не помеченные значком бота (🤖), принадлежат вашему собеседнику. Учитывайте это.{msg_separator}"

def message_your_next_tier_was_hown_to_the_partner(tier:int):
    return f"Вы поставили достаточное количество лайков, чтобы собеседнику было показан новый уровень вашего профиля (№ {tier}).{msg_separator}"

def message_your_full_profile_was_hown_to_the_partner():
    return f"Весь ваш профиль открыт для собеседника. Механика закончилась. Вы можете продолжить общение за рамками механик бота, либо использовать /next_please, чтобы попытаться найти ещё кого-то.{msg_separator}"

def message_i_do_not_know_what_to_do_with_this_message(): 
    return f"Я не знаю, что делать с этим сообщением. Возможно, какая-то комбинация команд /start (попробуйте её первой, особенно если до этого не использовали), /register или /unregister вам поможет.{msg_separator}"

def message_media_group_not_supported(): 
    return f"Медиа-группы (несколько картинок или других вложений в одном сообщении) не поддерживается в этой версии. Отправляйте эти штуки по одной в сообщении.{msg_separator}"

def message_message_you_trying_to_react_was_not_found(): 
    return f"Сообщение, которое вы пытаетесь [диз]лайкнуть, не найдено. Либо это глюк бота, либо вы выбрали сообщение не из текущей беседы (или это вообще сообщение бота, а не сообщение собеседника). Попробуйте её ещё раз (более внимательно и старательно).{msg_separator}"

def message_your_registration_completed_stop_send_messages():
    return f"Ваша регистрация завершена. Хватит слать сообщения! Либо объявите уже́ о готовности поговорить командой /start_chatting, либо отмените регистрацию командой /unregister.{msg_separator}"