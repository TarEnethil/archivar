from d20 import parse, RollError


# check that a given string can be parsed by the d20 parser
def is_valid_dice_string(dice):
    try:
        parse(dice)
    except RollError:
        return False

    return True
