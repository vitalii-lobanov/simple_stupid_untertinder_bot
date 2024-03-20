import random

# Temporary implementation. Will be replaced with a semantic-based ranking.
# List of supported emojis could be found here: 
# https://docs.aiogram.dev/uk-ua/latest/api/types/reaction_type_emoji.html#aiogram.types.reaction_type_emoji.ReactionTypeEmoji
class EmojiRank():
    emojis = {}
    def __init__(self):
        positive_emojis = {     #            
                                "❤": (8, 14),
                                "❤‍🔥": (7, 13),
                                "💋": (7, 12),
                                "💘": (7, 12),
                                "🔥": (6, 11),
                                "😍": (6, 10),
                                "🥰": (6, 10),
                                "😘": (6, 10),
                                "🤗": (6, 10),
                                "🤩": (6, 10),
                                "👍": (6, 9),
                                "👏": (5, 10),
                                "💔": (5, 9),
                                "😇": (5, 9),
                                "😢": (4, 8),
                                "😭": (4, 8),
                                "🎉": (4, 7),
                                "🍾": (4, 7),
                                "🐳": (4, 7),
                                "⚡": (4, 7),
                                "🥂": (4, 6),
                                "😈": (4, 6),
                                "🍓": (4, 6),
                                "💯": (3, 6),
                                "🍌": (4, 5),
                                "🤝": (2, 5),
                                "😎": (2, 4),
                                "🙊": (1, 4),
                                "🙈": (1, 4),
                                "🏆": (2, 3),
                                "😱": (2, 3),
                                "💅": (1, 3),
                                "🦄": (1, 2),
                                "🕊": (0, 1),
                                "👌": (0, 1),
                                "🤣": (0, 1),
                                "😁": (0, 1),
                                "🤓": (0, 1),
                                "👻": (0, 1),
                                "🤪": (0, 1),
                                "🙏": (0, 1),
                                "🙉": (0, 1),
                                "🎅": (0, 0.5),
                                "🎄": (0, 0.5),
                                "☃": (0, 0.5),
                                "👾": (0, 0.5),
                                "🫡": (0, 0.5),
                                "😨": (0, 0.5),
                          }

        negative_emojis = {
                                 "👎": (-35, -17),
                                "😡": (-20, -15),
                                "🤡": (-20, -15),
                                "🤬": (-20, -15),
                                "🤮": (-16, -12),
                                "🖕": (-14, -8),
                                "🥴": (-12, -14),
                                "🥱": (-3, -7),
                                "😐": (-4, -6),
                                "🤨": (-3, -5),
                                "💩": (-2, -6),
                          }



        neutral_emojis = {
                                "👀": (-0.5, 3),
                                "🌚": (-1, 3),
                                "🤯": (-3, 3),
                                "🤔": (-1, 2),
                                "✍": (-1, 1),
                                "🆒": (-1, 1),
                                "👨‍💻": (-1, 1),
                                "🎃": (-1, 1),
                                "🤷‍♂️": (-1, 1),
                                "🤷": (-1, 1),
                                "🤷‍♀️": (-1, 1),
                                "🤷‍♂": (-1, 1), 
                                "🤷‍♀": (-1, 1), 
                                "😴": (-1, 1),
                                "🌭": (-1, 1),
                                "💊": (-1, 1),
                                "🗿": (-1, 1),
                          }

        full_emojis_set = {**positive_emojis, **negative_emojis, **neutral_emojis}
       
        for emoji in full_emojis_set:
            self.emojis[emoji] = random.uniform(full_emojis_set[emoji][0], full_emojis_set[emoji][1])        

    # def get_rank(self, emoji: str):
    #     if emoji in self.emojis:
    #         return self.emojis[emoji]
    #     else:
    #         return None
            
    #TODO: this is hack for testing only, remove it, uncomment above
    def get_rank(self, emoji: str):
        return 5

full_emoji_set = ["👍", "👎", "❤", "🔥", "🥰", "👏", "😁", "🤔", "🤯", "😱", 
                  "🤬", "😢", "🎉", "🤩", "🤮", "💩", "🙏", "👌", "🕊", "🤡", 
                  "🥱", "🥴", "😍", "🐳", "❤‍🔥", "🌚", "🌭", "💯", "🤣", "⚡", 
                  "🍌", "🏆", "💔", "🤨", "😐", "🍓", "🍾", "💋", "🖕", "😈", 
                  "😴", "😭", "🤓", "👻", "👨‍💻", "👀", "🎃", "🙈", "😇", "😨", 
                  "🤝", "✍", "🤗", "🫡", "🎅", "🎄", "☃", "💅", "🤪", "🗿", 
                  "🆒", "💘", "🙉", "🦄", "😘", "💊", "🙊", "😎", "👾", "🤷‍♂",
                  "🤷", "🤷‍♀", "😡"]

ranker = EmojiRank()


for emoji in full_emoji_set:
    print (f"Emoji: {emoji}, rank: {ranker.get_rank(emoji)}")

