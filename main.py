from time import sleep
import random
import json
import math
import os

stopflag = False

MODE_NORMAL = True #answer with term
MODE_INVERTED = False #answer with def

mode = MODE_NORMAL

normal_chars = [chr(x) for x in range(ord("A"), ord("A") + 26)]
normal_chars += [chr(x) for x in range(ord("a"), ord("a") + 26)]
normal_chars += [str(x) for x in range(0, 9)]
normal_chars += ' '

def choose_set():
    files = os.listdir('sets')

    print("Found the following flashcard sets. If yours isn't here, add the .cards file to the sets folder.")
    for filename in files:
        if '.cards' in filename:
            print("Set: " + filename.removesuffix('.cards'))

    name = input("Type set name: ")
    if name + '.cards' in files:
        return name
    else:
        print("Set not found!")
        return False

def load_cards(name):
    cards = {}
    with open('sets/' + name + '.cards') as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        if ' | ' not in line:
            print("<" + line + "> did not contain ` | `")
        term, definition = line.split(' | ')
        if mode:
            cards[term] = definition
        else:
            cards[definition] = term

    b_chars = []
    for key, value in cards.items():
        for char in key + value:
            if char not in normal_chars:
                b_chars.append(char)

    return cards, b_chars

def load_progress(cards_name, cards):
    progress = {}
    if cards_name + '.progress' in os.listdir('sets'):
        if input("Use existing progress (y / n): ").lower()[0] == "y":
            with open('sets/' + cards_name + '.progress') as f:
                progress = json.load(f)

    delkeys = []
    addkeys = []
    for key in progress:
        if key not in cards:
            delkeys.append(key)
    for key in cards:
        if key not in progress:
            addkeys.append(key)

    for key in delkeys:
        progress.pop(key)
    for key in addkeys:
        progress[key] = {"mc": False, "or": False, "missed": False} #multichoice, open response

    return progress

def ask_mc(term, cards):
    global stopflag
    answers = [cards[term]]
    for i in range(0, 3):
        c = answers[0]
        while c in answers:
            c = random.choice(list(cards.values()))
        answers.append(c)

    random.shuffle(answers)

    print()
    print()
    print("  " + term)
    print()
    a1 = '1: ' + answers[0]
    a2 = '2: ' + answers[1]
    a3 = '3: ' + answers[2]
    a4 = '4: ' + answers[3]

    ldif = len(a1) - len(a2)

    print(a1, ' ' * -ldif + '  ', a3)
    print()
    print(a2, ' ' * ldif + '  ', a4)
    print()

    resp = ''
    while resp not in '1234' or resp == '':
        resp = input('> ')
        if resp == 'stop':
            stopflag = True
            return False
    return answers[int(resp) - 1] == cards[term]

def ask_or(term, cards, bchars):
    global stopflag
    print()
    print()
    print("  " + term)
    print()
    print()
    print()
    if len(bchars) != 0:
        for char in bchars:
            print(" " + char, end='')
        print()
    else:
        print()
    print()
    resp = input('> ')
    if resp == 'stop':
        stopflag = True
    return resp == cards[term]

def p_correct():
    print()
    print()
    print("+-----------------------------------------+")
    print("|                                         |")
    print("|                 Correct                 |")
    print("|                                         |")
    print("|                                         |")
    print("|                                         |")
    print("+-----------------------------------------+", end='')
    sleep(1)

def p_incorrect(canswer):
    print()
    print()
    print("+-----------------------------------------+")
    print("|                                         |")
    print("|                Incorrect                |")
    print("|                                         |")
    l = len(canswer)
    lb = len("-----------------------------------------")
    a, b = math.floor((lb - l) / 2), math.ceil((lb - l) / 2),
    print("|" + " " * a + canswer + " " * b + "|")
    print("|                                         |")
    print("+-----------------------------------------+", end='')
    input()

def p_done():
    print()
    print()
    print("+-----------------------------------------+")
    print("|                                         |")
    print("|                  Done!                  |")
    print("|                                         |")
    print("|                                         |")
    print("+-----------------------------------------+")


def study(cards, progress, bchars):
    while True:
        mc_list = []
        for key, value in progress.items():
            if not value["mc"]:
                mc_list.append(key)

        if len(mc_list) > 0:
            term = random.choice(mc_list)
            if ask_mc(term, cards):
                if stopflag:
                    break
                p_correct()
                if progress[term]["missed"]:
                    progress[term]["missed"] = False
                else:
                    progress[term]["mc"] = True
            else:
                if stopflag:
                    break
                p_incorrect(cards[term])
                progress[term]["missed"] = True

        else:
            or_list = []
            for key, value in progress.items():
                if not value["or"]:
                    or_list.append(key)

            if len(or_list) > 0:
                term = random.choice(or_list)
                if ask_or(term, cards, bchars):
                    p_correct()
                    if stopflag:
                        break
                    if progress[term]["missed"]:
                        progress[term]["missed"] = False
                    else:
                        progress[term]["or"] = True
                else:
                    if stopflag:
                        break
                    p_incorrect(cards[term])
                    progress[term]["missed"] = True

            else:
                p_done()
                break

def print_banner():
    print()
    print()
    print("+------------------------------------------+")
    print("|                                          |")
    print("|             Open Flashcards!             |")
    print("|                                          |")
    print("|                                          |")
    print("|          Press Enter to Start!           |")
    print("+------------------------------------------+", end='')
    input()

def main():
    cards_name = choose_set()
    if cards_name:
        cards, bchars = load_cards(cards_name)
        progress = load_progress(cards_name, cards)
        print_banner()
        study(cards, progress, bchars)
        if input("Save progress (y / n): ").lower()[0] == "y":
            with open('sets/' + cards_name + '.progress', 'w+') as f:
                json.dump(progress, f, indent=4)

if __name__ == '__main__':
    main()