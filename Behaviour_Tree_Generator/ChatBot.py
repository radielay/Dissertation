import copy
import random
import json
import Generator
import Encryption as Encrypt
from nltk.stem.lancaster import LancasterStemmer
stemmer = LancasterStemmer()

open("Conversation", "w").close()


"""-------------------------- Function for reading JSON Files ----------------------------------------------------"""


def read_json():
    # Read json file
    with open('intents.json') as file:
        data = json.load(file)

    return data


""" --------------------- Function for ADDING new answers to current behaviour tags -------------------------------"""


def add_intents(text):
    # Write the behaviour of the bot to a json file
    with open('intents.json', 'r+') as file:
        file.write(text)
        file.close()


""" ---------------------------------- INITIALIZE BOT -------------------------------------------------------------"""


class Brain:
    # Sorting JSON data
    def __init__(self):
        self.tag = ""
        self.patterns = []
        self.responses = []


def train_behaviour(data):
    behaviour = []

    # Loop through JSON file and extract behaviour data
    for intent in data['intents']:
        memory = Brain()

        category = copy.deepcopy(intent['tag'])
        memory.tag = category

        message = copy.deepcopy(intent['pattern'])
        memory.patterns = copy.deepcopy(message)

        response = copy.deepcopy(intent['responses'])
        memory.responses = copy.deepcopy(response)

        behaviour.append(memory)

    return behaviour


def set_up_bot():
    # Import json data
    data = read_json()

    # Train the bot
    intents = train_behaviour(data)

    return intents


def strip_input(user_input):
    # To avoid punctuational misunderstanding
    user_input = user_input.replace("?", "")
    user_input = user_input.replace("!", "")
    user_input = user_input.replace(",", "")
    user_input = user_input.replace(".", "")
    user_input = user_input.replace(":", "")
    user_input = user_input.replace(";", "")
    user_input = user_input.replace(")", "")
    user_input = user_input.replace("(", "")

    return user_input


def find_tag(user_input, intents):
    # Find the category of the user's input
    tag = ""
    for item in intents:
        if user_input in item.patterns:   # If the exact input exists
            tag = item.tag
        else:
            words = user_input.split(" ")   # If not, split the sentence into keywords
            for word in words:
                if word in item.patterns:   # Check for keywords
                    tag = item.tag
    return tag


def respond(category, intents):
    # Respond to certain categories
    for obj in intents:
        if obj.tag == category:
            r = random.randint(0, len(obj.responses) - 1)
            print(obj.responses[r])
            write_to_file("Bot: " + obj.responses[r] + "\n")


def feedback(intents):
    # When the service function has been executed, ask for feedback
    query = "Was I able to help you today?"
    write_to_file("Bot: " + query + "\n")
    print(query)

    answer = input("You:")
    write_to_file("User: " + answer + "\n")

    tag = find_tag(answer, intents)
    if tag == "yes":
        respond("thanks", intents)
    elif tag == "no":
        print("I seem to have failed my task.")
        print("Would you like to speak to a member of staff?")

        new_inp = input("You: ")
        if new_inp == "yes":
            respond("human_needed", intents)
        else:
            respond("goodbye", intents)
    else:
        respond("goodbye", intents)


def write_to_file(text):
    with open('Conversation', 'a') as chat_file:
        chat_file.write(text)
        chat_file.close()


""" --------------------------------- BOT ABILITIES ---------------------------------------------------------------"""


def strip_user_input(user_input, x):
    inp = user_input.replace(x, "")

    return inp


def confirm_intent(user_input, intents):
    # Use if the user's input is unclear
    inp = user_input.replace("yes", "")
    inp = inp.replace("no", "")

    if len(inp) > 1:
        tag = find_tag(inp, intents)

        if tag == "Tracking":
            return tag
        elif tag == "":
            return tag
        elif tag == "no":
            respond("unhappy", intents)
        else:
            respond(tag, intents)
    else:
        if "yes" in user_input:
            respond("happy", intents)
        elif "no" in user_input:
            respond("unhappy", intents)


def confirm_politeness(user_input, tag, intents):
    """ Strip the input from any form of politeness for more accurate answers """
    data = read_json()
    for obj in data['intents']:
        if obj['tag'] == tag:
            patterns = copy.deepcopy(obj['pattern'])

    inp = user_input
    for n in range(0, len(patterns)):
        x = patterns[n]
        inp = strip_user_input(inp, x)  # Strip the input from any form of politeness for better grasp

    # Determine whether there is a second meaning to the user's input
    if len(inp) > 1:
        new_topic = confirm_intent(inp, intents)

        if new_topic == "":
            respond(tag, intents)
        elif new_topic == "Tracking":
            return new_topic
    else:
        respond(tag, intents)


def learn(user_input, intents):
    # Learn unrecognized input by consulting the user
    message = "Sorry, I didn't get that!"
    write_to_file("Bot: " + message + "\n")
    print(message)

    for item in intents:
        write_to_file("Bot: " + "Was that a " + item.tag + "?\n")
        print("Was that a", item.tag, "?")

        new_input = input("You: ")
        write_to_file("User: " + new_input + "\n")
        new_input = new_input.lower()
        if new_input == "quit":
            break
        elif new_input == "stop":
            break

        new_tag = find_tag(new_input, intents)
        if new_tag == "yes":
            data = read_json()
            for obj in data['intents']:
                if obj['tag'] == item.tag:
                    obj['pattern'].append(user_input)
                    data = json.dumps(data)
                    add_intents(data)
                    print("Noted!")
                    break
            break
        elif new_tag == "stop":
            break


def activate_service(user_input, tag, intents, trigger_tag):
    """ Activate the chat bot"""
    service = True
    user_input = user_input.lower()

    if tag == "":
        learn(user_input, intents)
        respond("chatter_answer", intents)

    elif tag == trigger_tag:
        return tag

    elif tag == "yes":
        confirm_intent(user_input, intents)
    elif tag == "no":
        confirm_intent(user_input, intents)
    elif tag == "thanks":
        new_tag = confirm_politeness(user_input, tag, intents)
        if new_tag == trigger_tag:
            service = new_tag
    elif tag == "stop":
        service = False

    else:
        respond(tag, intents)
        if tag == "goodbye":
            service = False
        if tag == "human_needed":
            service = False

    return service


""" ----------------------------  NOT USED IN BT_Generator ------------ Testing just chat bot component -----------"""


def startup():
    # Get behaviour structure
    intents = set_up_bot()
    print(" ")
    print("Welcome to the Delivery Tracking Services Bot. Should you need human assistance, just write 'quit'.")

    running = True
    while running:
        user_input = input("You: ")
        write_to_file("User: " + user_input + "\n")
        user_input = strip_input(user_input).lower()

        if user_input == "quit":
            feedback(intents)
            break
        else:
            tag = find_tag(user_input, intents)

            if tag == "tracking":
                print("Tag: ", tag)
                break

            elif tag == "":
                learn(user_input, intents)
                respond("chatter_answer", intents)

            elif tag == "yes":
                confirm_intent(user_input, intents)
            elif tag == "no":
                confirm_intent(user_input, intents)
            elif tag == "thanks":
                confirm_politeness(user_input, tag, intents)

            elif tag == "stop":
                break
            else:
                respond(tag, intents)
                if tag == "goodbye":
                    break
                if tag == "human_needed":
                    break


# startup()
# Encrypt.main()
