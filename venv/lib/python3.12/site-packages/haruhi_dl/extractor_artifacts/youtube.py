
def mess(a, b):
    c = a[0]
    a[0] = a[b % len(a)]
    a[b % len(a)] = c
    return a


def _decrypt_signature_protected(sig):
    a = list(sig)
    a = mess(a, 23)
    a.reverse()
    a = mess(a, 49)
    a = mess(a, 39)
    a = a[2:]
    return ''.join(a)
