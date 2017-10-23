

# total bullshit. No restriction on values of array needed
def find_duplicate(array):

    for i, e1 in enumerate(array):
        for j, e2 in enumerate(array[:i]):
            if e1 == e2:
                return e1

    return -1

print(find_duplicate([2, 3, 3, 4, 5, 2]))
print(find_duplicate([2, 3, 4, 5, ]))


# Easy to understand bullshit. No restriction on values of array needed
def find_duplicate(array):

    my_set = set()
    for i, e in enumerate(array):
        if e in my_set:
            return e
        my_set.add(e)

    return -1

print(find_duplicate([2, 3, 3, 4, 5, 2]))
print(find_duplicate([2, 3, 4, 5, ]))


# Easy to understand bullshit. No restriction on values of array needed
def find_duplicate(array):

    my_list = list()
    for i, e in enumerate(array):
        if e in my_list:
            return e
        my_list.append(e)

    return -1

print(find_duplicate([2, 3, 3, 4, 5, 2]))
print(find_duplicate([2, 3, 4, 5, ]))


# next to total bullshit
def find_duplicate(array):

    for i, e1 in enumerate(array):
        if e1 in array[:i]:
            return e1

    return -1


print(find_duplicate([2, 3, 3, 4, 5, 2]))
print(find_duplicate([2, 3, 4, 5, ]))


# bit better. No restriction on values of array needed
def find_duplicate(array):

    my_set = set()
    for i, e in enumerate(array):
        if e in my_set:
            return e
        my_set.add(e)

    return -1


print(find_duplicate([2, 3, 3, 4, 5, 2]))
print(find_duplicate([2, 3, 4, 5, ]))


# Better. More readable, O(n) additional space complexity. No restriction on values of array needed
#def find_duplicate(array):

#    has_value =
#    for e in array:
#        if array[abs(e)-1] < 0:
#            return abs(e)
#        array[abs(e)-1] *= -1

#    return -1

# Awesomeness: having number values only between 1 and the index!
def find_duplicate(array):

    for e in array:
        if array[abs(e)-1] < 0:
            return abs(e)
        array[abs(e)-1] *= -1

    return -1


print(find_duplicate([2, 3, 3, 4, 5, 2]))
print(find_duplicate([2, 3, 4, 1]))


#[2, 3, 3, 4, 5, 2]

#[2, -3, 3, 4, 5, 2]

#[2, -3, -3, 4, 5, 2]
