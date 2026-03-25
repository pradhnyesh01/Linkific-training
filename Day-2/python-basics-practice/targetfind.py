target = 25
nums = [1, 4, 9, 16, 25, 36, 49, 64, 81, 100]
i=0
while (i <= len(nums) and target != nums[i]):
    i+=1
if i<len(nums):
    print(target, i)
else:
    print("Target not found")