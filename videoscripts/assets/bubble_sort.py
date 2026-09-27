arr = [3, 2, 4, 6, 1]
n = len(arr)

for i in reversed(range(n)):
    swapped = False
    for j in range(i):
        if arr[j] > arr[j + 1]:
            swapped = True
            arr[j], arr[j + 1] = arr[j + 1], arr[j]
    if not swapped:
        break
