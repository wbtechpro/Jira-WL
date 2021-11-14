
def split_list(list, part_len):
    # For item i in a range that is a length of part_len,
    for i in range(0, len(list), part_len):
        # Create an index range for list of n items:
        yield list[i:i + part_len]
