def ccc():
    arr = [2,4,6,3,19,7]
    target = arr[-1]
    for i in range(len(arr)-1):
        if arr[i] + arr[i+1] == target:
            return '%d, %d' % (i,int(i+1))
        if arr[i] + arr[i+2] == target:
            return '%d, %d' % (i,int(i+2))
print(ccc())