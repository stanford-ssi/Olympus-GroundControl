


def unit_factor(string):
    if string is None:
        return 1

    from_unit, to_unit = string.split("->")

    conv = {}
    conv["Pa->psi"] = 0.000145038
    conv["N->kg"] = 1/9.81

    assert string in conv

    return conv[string]



