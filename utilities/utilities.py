import math


def sig_fig(num, s_f):
    return round(num, s_f - int(math.floor(math.log10(abs(num)))) - 1)  # method for significant figures


def number_suffix(num):  # add a suffix to numbers to make it easier to read
    if num < 1000:
        return sig_fig(num, 6)  # no prefix

    if num < 1000000:
        return insert_string(str(sig_fig(num, 5))[:-1], ".", -2) + "k"  # thousand

    if num < 1000000000:
        return insert_string(str(sig_fig(num, 5))[:-4], ".", -2) + "M"  # million

    if num < 1000000000000:
        return insert_string(str(sig_fig(num, 5))[:-7], ".", -2) + "B"  # billion

    if num < 1000000000000000:
        return insert_string(str(sig_fig(num, 5))[:-10], ".", -2) + "T"  # trillion


def insert_string(string, insert, index):
    return string[:index] + insert + string[index:]  # insert a string into a string
