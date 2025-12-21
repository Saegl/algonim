arr = [4, 2, 1, 3, 9, 2, 5]
max_elem = -1

for i in range(len(arr)):
    if arr[i] > max_elem:
        max_elem = arr[i]

print(max_elem)
