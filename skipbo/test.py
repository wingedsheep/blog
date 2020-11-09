allowed_action = [1, 2, 5, 8]
action_values = [4, 1, 2, 3, 4, 5, 6, 7, 8, 9]
adjusted_values = [value if index in allowed_action else 0 for index, value in enumerate(action_values)]
print(adjusted_values)