def getScore(user, ai):
    if user == ai:
        return 0
    elif (user == "rock") and (ai == "paper"):
        return -1
    elif (user == "rock") and (ai == "scissors"):
        return 1
    elif (user == "paper") and (ai == "scissors"):
        return -1
    elif (user == "paper") and (ai == "rock"):
        return 1
    elif (user == "scissors") and (ai == "rock"):
        return -1
    elif (user == "scissors") and (ai == "paper"):
        return 1
