import math


def sig_fig(num, s_f):
    return round(num, s_f - int(math.floor(math.log10(abs(num)))) - 1)


def number_suffix(num):
    if num < 1000:
        return sig_fig(num, 6)

    if num < 1000000:
        return insert_string(str(sig_fig(num, 5))[:-1], ".", -2) + "k"

    if num < 1000000000:
        return insert_string(str(sig_fig(num, 5))[:-4], ".", -2) + "M"

    if num < 1000000000000:
        return insert_string(str(sig_fig(num, 5))[:-7], ".", -2) + "B"

    if num < 1000000000000000:
        return insert_string(str(sig_fig(num, 5))[:-10], ".", -2) + "T"


def insert_string(string, insert, index):
    return string[:index] + insert + string[index:]
