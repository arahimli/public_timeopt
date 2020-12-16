list = []
list_all = []
for i in range(1,601):
    for j in range(1,601):
        if i == j or i>j:
            pass
        else:
            list.append((i,j))
        list_all.append((i,j))

if (557, 196) in list:
    print('he')
else:
    print('yox')

print(len(list))
print(len(list_all))
# print(list)