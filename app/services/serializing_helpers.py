from typing import Any, Dict, List, Optional, Union
import os
from aiogram import types


#TODO: optional as 'None' handler in function output types. 
#TODO: find the way to more strictly type checking
def message_poll_to_dict(poll: types.Poll) -> Optional[Dict[str, Any]]:
    if poll is not None:
        return {
            "id": poll.id,
            "question": poll.question,
            "options": [{"text": option.text, "voter_count": option.voter_count} for option in poll.options],
            "total_voter_count": poll.total_voter_count,
            "is_closed": poll.is_closed,
            "is_anonymous": poll.is_anonymous,
            "type": poll.type,
            "allows_multiple_answers": poll.allows_multiple_answers,
            "explanation": poll.explanation,
            "explanation_entities": message_entities_to_dict(poll.explanation_entities) if poll.explanation_entities else None,
            "open_period": poll.open_period,
            "close_date": poll.close_date,
        }
    else:
        return None

def get_multimedia_paths_from_message(message: types.Message) -> dict:
    return {
        "audio": message.audio.file_id if message.audio else None,
        "document": message.document.file_id if message.document else None,
        "photo": message.photo[-1].file_id if message.photo else None,
        "sticker": message.sticker.file_id if message.sticker else None,
        "video": message.video.file_id if message.video else None,
        "voice": message.voice.file_id if message.voice else None,
        "video_note": message.video_note.file_id if message.video_note else None,
        "animation": message.animation.file_id if message.animation else None,
    }


def location_to_dict(location: types.Location) -> Dict[str, float]:
    return {
        "longitude": location.longitude,
        "latitude": location.latitude,
    }




def message_entities_to_dict(
    entities: List[types.MessageEntity],
) -> Optional[List[Dict[str, Union[str, int, Optional[Dict[str, Any]]]]]]:
    return (
        [
            {
                "type": entity.type,
                "offset": entity.offset,
                "length": entity.length,
                "url": entity.url,
                "user": entity.user.to_dict() if entity.user else None,
                "language": entity.language,
            }
            for entity in entities
        ]
        if entities
        else None
    )


def link_preview_options_to_dict(
    link_preview_options: Optional[types.LinkPreviewOptions],
) -> Optional[Dict[str, Union[bool, str, None]]]:
    if link_preview_options is not None:
        is_disabled = (
            link_preview_options.is_disabled
            if isinstance(link_preview_options.is_disabled, bool)
            else False
        )
        return {
            "is_disabled": is_disabled,
            "url": link_preview_options.url
            if isinstance(link_preview_options.url, str)
            else None,
        }
    return None

def extract_file_id_from_path(file_path: str) -> str:
    filename = os.path.basename(file_path)      
    file_id_parts = filename.split('_')[1:]
    file_id = '_'.join(file_id_parts)
    return file_id