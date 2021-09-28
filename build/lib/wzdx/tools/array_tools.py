

# return dimension of list (only analyzing 0th index)
def dim(a):
    """Return dimensions of list and all non-empty sub-lists ([[1,2]] -> [1,2])"""
    if not type(a) == list or len(a) == 0:
        return []
    return [len(a)] + dim(a[0])


def get_2d_list(l):
    """Convert an n dimensional list to a 2 dimensional list by taking final 
    2 dimensions at index 0"""
    dimensions = dim(l)
    index = len(dimensions) - 2
    if index == 1:
        return l[0]
    elif index == 2:
        return l[0][0]
    elif index == 0:
        return l
    else:
        return None
