from scipy import stats
import numpy as np

def box_cox_scale_single_value(value_to_normalize, values_list, target_range_min=0, target_range_max=9):
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
    scale = lambda x: (x - min_transformed) / (max_transformed - min_transformed) * (target_range_max - target_range_min) + target_range_min

    # Scale the absolute value of the value to normalize, find its position in the original list and scale accordingly
    abs_value_to_normalize = abs(value_to_normalize)
    if value_to_normalize > 0 and positive_values:
        transformed_value_to_normalize = scale(positive_transformed[positive_values.index(abs_value_to_normalize)])
    elif value_to_normalize < 0 and negative_values:
        transformed_value_to_normalize = -scale(negative_transformed[negative_values.index(abs_value_to_normalize)])
    else:
        # If value_to_normalize is zero or not in the list, return a scaled value of zero
        transformed_value_to_normalize = scale(min_transformed) if value_to_normalize >= 0 else -scale(min_transformed)

    return transformed_value_to_normalize

# Example usage:
raw_rank_values = [-24.85, -19.69, -17.62, -15.89, 0.00, 0.01, 1.00]
scaled_values = [box_cox_scale_single_value(x, raw_rank_values) for x in raw_rank_values]
print(scaled_values)