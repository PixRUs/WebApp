
def get_probability(odd:str):
    if odd.startswith("-"):
        odd = odd[1:]
        odd = int(odd)
        return odd / (odd + 100)
    else:
        odd = int(odd)
        return 100 / (odd + 100)