import random
from utils.d_debug import d_logger
import math
import numpy as np
import math

from scipy.stats import boxcox
from scipy import stats

def min_max_scaling(value_to_normalize, values_list, target_range_min=0, target_range_max=9):
    min_value = min(values_list)
    max_value = max(values_list)
    
    if min_value == max_value:
        raise ValueError("Minimum and maximum values cannot be the same for min-max normalization.")
    
    # Normalize the value to the 0-1 range
    normalized_value = (value_to_normalize - min_value) / (max_value - min_value)
    
    # Scale to the target range
    scaled_value = normalized_value * (target_range_max - target_range_min) + target_range_min
    
    return scaled_value



def z_score_scaling(values_list, value, target_range_min = 0, target_range_max = 9):
    mean = sum(values_list) / len(values_list)
    std_dev = (sum((x - mean) ** 2 for x in values_list) / len(values_list)) ** 0.5
    normalized_value = (value - mean) / std_dev
    min_z_score = (min(values_list) - mean) / std_dev
    shifted_value = normalized_value - min_z_score
    scale = target_range_max - target_range_min
    shift_scale = (max(values_list) - mean) / std_dev - min_z_score 
    scaled_value = shifted_value / shift_scale * scale
    return scaled_value

def calculate_lambda(values_list):
    min_value = min(values_list)
    if min_value < 0:
        lambda_value = abs(min_value) + 1
    else:
        lambda_value = 1  # or some small positive value to avoid log(0)
    return lambda_value    

def logarithmic_scaling(value, values_list, target_range_min = 0.00001, target_range_max=9, base=2000):
    
    source_range_min = min(values_list)
    source_range_max = max(values_list)

    log_min = math.log(source_range_min, base)
    log_max = math.log(source_range_max, base)

    lambda_value = calculate_lambda(values_list)

    if value < 0:
        log_value =  -math.log(abs(value) + lambda_value, base)
    else:
        log_value = math.log(value + lambda_value, base)

   
    normalized_log = (log_value - log_min) / (log_max - log_min)
    scaled_value = normalized_log * (target_range_max - target_range_min) + target_range_min
    return scaled_value



def robust_scaling(value_to_normalize, values_list, target_range_min=0, target_range_max=9):

    # Calculate the median
    median = np.median(values_list)
    
    # Calculate the interquartile range (IQR)
    Q1 = np.percentile(values_list, 25)
    Q3 = np.percentile(values_list, 75)
    iqr = Q3 - Q1
    
    if iqr == 0:
        raise ValueError("IQR must be non-zero for robust scaling.")
    
    # Robust scaling transformation
    scaled_value = (value_to_normalize - median) / iqr
    
    # Scale and shift the value to fit the target range
    # Add target_range_min to shift the range starting from target_range_min
    scaled_value = (scaled_value * (target_range_max - target_range_min) / 2) + ((target_range_max + target_range_min) / 2)
    
    return scaled_value
def box_cox_scaling(value_to_normalize, values_list, target_range_min=0, target_range_max=9):
    # Separate the values into positive and negative values, make sure to avoid zero
    positive_values = [x for x in values_list if x > 0]
    negative_values = [-x for x in values_list if x < 0]  # Make negative values positive

    # Apply Box-Cox transformation separately on positive and negative values
    if positive_values:
        positive_transformed, _ = stats.boxcox(positive_values)
    else:
        positive_transformed = np.array([])  # Use an empty NumPy array for consistency

    if negative_values:
        negative_transformed, _ = stats.boxcox(negative_values)
    else:
        negative_transformed = np.array([])

    # Combine the transformed values if both arrays are not empty
    if positive_transformed.size > 0 and negative_transformed.size > 0:
        all_transformed = np.concatenate((negative_transformed, positive_transformed))
    else:
        all_transformed = positive_transformed if positive_transformed.size > 0 else negative_transformed

    # Handle the case where all values are constant or there are no values
    if all_transformed.size == 0 or np.all(all_transformed == all_transformed[0]):
        return value_to_normalize  # Return the original value or handle differently

    # Scale the transformed values to the target range
    min_transformed = np.min(all_transformed)
    max_transformed = np.max(all_transformed)
    def scale(x):
        return (x - min_transformed) / (max_transformed - min_transformed) * (target_range_max - target_range_min) + target_range_min

    # Scale the absolute value of the value to normalize, find its position in the original list and scale accordingly
    abs_value_to_normalize = abs(value_to_normalize)
    # Find the index of the closest value in positive_values to abs_value_to_normalize for positive numbers
    if value_to_normalize > 0 and positive_values:
        closest_index = np.argmin([abs(x - abs_value_to_normalize) for x in positive_values])
        transformed_value_to_normalize = scale(positive_transformed[closest_index])
    elif value_to_normalize < 0 and negative_values:
        # For negative numbers, you should find the closest value in negative_values
        closest_index = np.argmin([abs(x - abs_value_to_normalize) for x in negative_values])
        transformed_value_to_normalize = -scale(negative_transformed[closest_index])
    else:
        # If value_to_normalize is zero or not in the list, return a scaled value of zero
        transformed_value_to_normalize = scale(min_transformed) if value_to_normalize >= 0 else -scale(min_transformed)

    return transformed_value_to_normalize

def unit_vector_single_value_scaling(value_to_normalize, values_list, target_range_min=0, target_range_max=9):
    # Add the value to normalize to the list of values to treat it as part of the vector
    extended_values = np.array(values_list + [value_to_normalize])
    
    # Perform unit vector normalization on the extended vector
    norm = np.linalg.norm(extended_values)
    unit_vector = extended_values / norm
    
    # The last element of the unit vector corresponds to the normalized value of interest
    normalized_value = unit_vector[-1]
    
    # Scale to the target range
    # Here we adjust the range based on the sign of the input value
    if value_to_normalize >= 0:
        scaled_value = normalized_value * (target_range_max - target_range_min) / 2 + (target_range_max + target_range_min) / 2
    else:
        scaled_value = normalized_value * (target_range_max - target_range_min) / 2 - (target_range_max + target_range_min) / 2
    
    return scaled_value

def max_absolute_scaling(value_to_normalize, values_list, target_range_min=0, target_range_max=9):
    # Find the maximum absolute value from the list
    max_abs_value = max(abs(value) for value in values_list)
    
    if max_abs_value == 0:
        raise ValueError("The maximum absolute value must be non-zero for scaling.")
    
    # Apply max absolute scaling to the value to normalize
    scaled_value = (value_to_normalize / max_abs_value) * (target_range_max - target_range_min)
    
    # Check if the original value to normalize is negative or positive
    # Then adjust the scaled value to be within the target range while keeping the sign
    if value_to_normalize < 0:
        scaled_value = ((scaled_value - 1) / 2) * (target_range_max - target_range_min) + target_range_min
    else:
        scaled_value = ((scaled_value + 1) / 2) * (target_range_max - target_range_min) + target_range_min
    
    return scaled_value

def power_scaling(value_to_normalize, values_list, power, target_range_min=0.001, target_range_max=9):
    if power <= 0:
        raise ValueError("Power must be positive for power scaling.")

    # Ensure power is an integer to avoid complex results
    power = int(power)
    
    # Find minimum and maximum values from the transformed list
    transformed_max = max(abs(v) for v in values_list)**power
    transformed_min = min(abs(v) for v in values_list)**power

    # Apply power transformation to the value to normalize
    # and preserve the sign by multiplying with it after transformation
    sign = 1 if value_to_normalize >= 0 else -1
    transformed_value_to_normalize = sign * (abs(value_to_normalize)**power)

    # Normalize the transformed value to a 0-1 range
    normalized_value = ((transformed_value_to_normalize - transformed_min) / 
                        (transformed_max - transformed_min))

    # Scale to the target range, preserving the sign of the input value
    scaled_value = normalized_value * (target_range_max - target_range_min) + target_range_min

    return scaled_value

# Temporary implementation. Will be replaced with a semantic-based ranking.
# List of supported emojis could be found here:
# https://docs.aiogram.dev/uk-ua/latest/api/types/reaction_type_emoji.html#aiogram.types.reaction_type_emoji.ReactionTypeEmoji
class EmojiRank:
    emojis = {}

    def __init__(self) -> None:
        positive_emojis = {  #
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
            "👿": (0, 0), #TODO: remove!
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

        self.full_emojis_set = {**positive_emojis, **negative_emojis, **neutral_emojis}

        for emoji in self.full_emojis_set:
            self.emojis[emoji] = random.uniform(
                self.full_emojis_set[emoji][0], self.full_emojis_set[emoji][1]
            )
        self.min_possible_rank = 0.65
        self.max_possible_rank = max(value[1] for value in self.full_emojis_set.values())

    def get_rank(self, emoji: str) -> float:
        # d_logger.debug("D_logger")
        if emoji in self.emojis:
            raw_rank = self.emojis[emoji]
            values_range = [self.min_possible_rank, self.max_possible_rank]
            scaled_rank = logarithmic_scaling(raw_rank, values_range)
            if scaled_rank > 9:
                scaled_rank = 9
            if scaled_rank < -9:
                scaled_rank = -9
            return scaled_rank
        else:
            raise ValueError(f"Emoji not found: {emoji}")

    # # TODO: this is hack for testing only, remove it, uncomment above
    # def get_rank(self, emoji: str):
    #     return 5


full_emoji_set = [
    "👍",
    "👎",
    "❤",
    "🔥",
    "🥰",
    "👏",
    "😁",
    "🤔",
    "🤯",
    "😱",
    "🤬",
    "😢",
    "🎉",
    "🤩",
    "🤮",
    "💩",
    "🙏",
    "👌",
    "🕊",
    "🤡",
    "🥱",
    "🥴",
    "😍",
    "🐳",
    "❤‍🔥",
    "🌚",
    "🌭",
    "💯",
    "🤣",
    "⚡",
    "🍌",
    "🏆",
    "💔",
    "🤨",
    "😐",
    "🍓",
    "🍾",
    "💋",
    "🖕",
    "😈",
    "😴",
    "😭",
    "🤓",
    "👻",
    "👨‍💻",
    "👀",
    "🎃",
    "🙈",
    "😇",
    "😨",
    "🤝",
    "✍",
    "🤗",
    "🫡",
    "🎅",
    "🎄",
    "☃",
    "💅",
    "🤪",
    "👿", # TODO: remove
    "🗿",
    "🆒",
    "💘",
    "🙉",
    "🦄",
    "😘",
    "💊",
    "🙊",
    "😎",
    "👾",
    "🤷‍♂",
    "🤷",
    "🤷‍♀",
    "😡",
]

ranker = EmojiRank()




# # Assuming `ranker` is an instance of EmojiRank and `get_rank` returns the rank for an emoji
# emoji_rankings = [(emoji, ranker.get_rank(emoji)) for emoji in full_emoji_set]
# sorted_emoji_rankings = sorted(emoji_rankings, key=lambda x: x[1])  # Sort by rank

# for emoji, rank in sorted_emoji_rankings:
#     print(f"{emoji}: {rank}")


# For the testing purposes

# for emoji in full_emoji_set:
#     rank = ranker.get_rank(emoji)
#     print(f"{emoji}: {rank}")

# full_ranks_set = []
# for i in np.arange(0.5, 14.5, 0.5):
#    full_ranks_set = full_ranks_set + [i]

# values_list = full_ranks_set

# # print(f"{'Value':<10}{'Min-Max':<15}{'Z-Score':<15}{'Logarithmic':<15}{'Robust':<15}{'Box-Cox':<15}{'Unit Vector':<15}{'Max Abs':<15}{'Power':<15}")
# # for rank in values_list:    
# #     min_max_scaled_value = min_max_scaling(rank, values_list)
# #     z_score_scaled_value = z_score_scaling(values_list, rank)
# #     logarithmic_scaled_value = logarithmic_scaling(rank, values_list)
# #     robust_scaled_value = robust_scaling(rank, values_list)
# #     box_cox_scaled_value = box_cox_scaling(rank, values_list)
# #     unit_vector_single_value_scaled_value = unit_vector_single_value_scaling(rank, values_list)
# #     max_absolute_scaled_value = max_absolute_scaling(rank, values_list)
# #     power_scaled_value = power_scaling(rank, values_list, 3)
# #     print(f"{rank:<10}{min_max_scaled_value:<15.2f}{z_score_scaled_value:<15.2f}{logarithmic_scaled_value:<15.2f}{robust_scaled_value:<15.2f}{box_cox_scaled_value:<15.2f}{unit_vector_single_value_scaled_value:<15.2f}{max_absolute_scaled_value:<15.2f}{power_scaled_value:<15.2f}")

# # print(f"{'Emoji':<8}{'Raw Rank':<10}{'Min-Max':<15}{'Z-Score':<15}{'Logarithmic':<15}{'Robust':<15}{'Box-Cox':<15}{'Unit Vector':<15}{'Max Abs':<15}{'Power':<15}")
# # Prepare a list to hold all the rows of data
# data_rows = []

# # Gather the data for each emoji
# for emoji in full_emoji_set:
#     raw_rank = ranker.get_rank(emoji)
#     negative_flag = -1 if raw_rank < 0 else 1
#     rank = abs(raw_rank)

#     min_max_scaled_value = min_max_scaling(raw_rank, values_list)
#     z_score_scaled_value = z_score_scaling(values_list, raw_rank)
#     logarithmic_scaled_value = logarithmic_scaling(raw_rank, values_list)
#     robust_scaled_value = robust_scaling(raw_rank, values_list)
#     box_cox_scaled_value = box_cox_scaling(raw_rank, values_list)
#     unit_vector_single_value_scaled_value = unit_vector_single_value_scaling(raw_rank, values_list)
#     max_absolute_scaled_value = max_absolute_scaling(raw_rank, values_list)
#     power_scaled_value = power_scaling(raw_rank, values_list, 1.001)

#     # Store the data in a tuple
#     data_rows.append((
#         emoji,
#         raw_rank,
#         min_max_scaled_value,
#         z_score_scaled_value,
#         logarithmic_scaled_value,
#         robust_scaled_value,
#         box_cox_scaled_value,
#         unit_vector_single_value_scaled_value,
#         max_absolute_scaled_value,
#         power_scaled_value
#     ))

# # Now sort the data by the raw_rank
# sorted_data_rows = sorted(data_rows, key=lambda x: x[1])

# # Print the header of the table
# print(f"{'Emoji':<8}{'Raw Rank':<10}{'Min-Max':<15}{'Z-Score':<15}{'Logarithmic':<15}{'Robust':<15}{'Box-Cox':<15}{'Unit Vector':<15}{'Max Abs':<15}{'Power':<15}")

# # Print the sorted data rows
# for row in sorted_data_rows:
#     emoji, raw_rank, min_max, z_score, logarithmic, robust, box_cox, unit_vector, max_abs, power = row
#     print(f"{emoji:<8}{raw_rank:<10.2f}{min_max:<15.2f}{z_score:<15.2f}{logarithmic:<15.2f}{robust:<15.2f}{box_cox:<15.2f}{unit_vector:<15.2f}{max_abs:<15.2f}{power:<15.2f}")