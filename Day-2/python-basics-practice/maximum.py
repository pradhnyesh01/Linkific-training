scores = [88, 92, 79, 95, 81]
highest = scores[0]

for s in scores:
    if s > highest:
        highest = s

print(f"The top score was: {highest}")