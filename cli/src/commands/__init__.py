from builtins import input


def confirm(message="Confirm"):
    prompt = message + " [y/n]:\n"

    while True:
        ans = input(prompt)
        if ans not in ["y", "Y", "n", "N"]:
            print("please enter y or n.")
            continue
        if ans in ["y", "Y"]:
            return True
        if ans in ["n", "N"]:
            return False
