from typing import Final, final 

@final
class MessageTiersCount:
    MESSAGE_TIERS_COUNT: Final[int] = 8

@final
class ProfileDisclosureTiersScoreLevels:
    PROFILE_DISCLOSURE_TIER_LEVELS: Final[list[float]]= [0, 1, 2, 3, 4, 5, 6, 7]
    

message_tiers_count = MessageTiersCount()
profile_disclosure_tiers_score_levels = ProfileDisclosureTiersScoreLevels()

if len(profile_disclosure_tiers_score_levels.PROFILE_DISCLOSURE_TIER_LEVELS) != message_tiers_count.MESSAGE_TIERS_COUNT:
    raise ValueError("Profile disclosure tiers score levels count must be equal to message tiers count")