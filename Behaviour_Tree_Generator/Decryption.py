import hashlib
import random
import string


def read_file():
    chars = ""
    with open("Hash", "r") as file:   # Read the hashed string
        for line in file:
            chars += line

    file.close()
    return chars


def read_code():   # Read the key for interpretation
    key = []
    with open("Code", "r") as file:
        for line in file:
            for code in line.split():
                key.append(code)
    file.close()
    return key


def get_letters(big_hash):
    hash_letters = []

    length = int(len(big_hash)/64)
    position = 0
    max_len = 64
    for char in range(0, length):
        letter = ""
        for i in range(position, max_len):    # Divide the big hash back into normal hashes of chars
            letter += big_hash[i]
        position += 64
        max_len += 64

        hash_letters.append(letter)     # Gather them in a list

    return hash_letters


def assort(hashed_letter):
    temp = []
    shuffled = []

    size = len(hashed_letter)
    for index in range(0, size):   # Reverse every hashed letter
        if index == 8:
            temp.append(hashed_letter[index])
        elif index == 9:
            temp.append(hashed_letter[index])
        elif index == 14:
            temp.append(hashed_letter[index])
        elif index == 15:
            temp.append(hashed_letter[index])
        elif index == 22:
            temp.append(hashed_letter[index])
        elif index == 23:
            temp.append(hashed_letter[index])
        else:
            shuffled.append(hashed_letter[index])

    for i in range(0, len(temp)):  # Gather the original chars
        shuffled.append(temp[i])

    original = ""
    for i in range(0, len(shuffled)):   # Put the hash back together
        original += shuffled[i]

    return original


def get_symbols():
    punctuation = []
    run = True
    while run:
        generate = random.choice(string.punctuation)
        hashed = hashlib.sha256(str.encode(generate)).hexdigest()

        if hashed not in punctuation:
            punctuation.append(hashed)
            punctuation.append(generate)

        if len(punctuation) == 64:
            break

    return punctuation


def decode(target, symbols):
    char = ""
    run = True
    while run:
        generate = random.choice(string.ascii_letters)    # Generate random guesses (of letters)
        hashed = hashlib.sha256(str.encode(generate)).hexdigest()   # Hash them to check if they match

        if hashed == target:                                        # the targeted hash
            char = generate
            break

        if target in symbols:
            position = symbols.index(target) + 1
            char = symbols[position]
            break

    return char


def transform(hashed_letters, symbols):
    letters = []
    for letter in range(0, len(hashed_letters)):    # Transform hashed letters into plain text letters,
        reverse = assort(hashed_letters[letter])    # by putting the hashes back together
        plain_text = decode(reverse, symbols)                # and decoding them
        letters.append(plain_text)

    return letters


def get_word(letters, key):
    words = []
    plain_text = ""

    for n in range(0, len(key)):
        word = ""
        num_letters = int(key[n])     # For every word, get its length
        for i in range(0, num_letters):
            word += letters[0]          # Put the word back together from the bag of letters
            letters.remove(letters[0])   # Remove the taken words out of the bag

        # words.append(word)    # Gather all the words
        if word == "User:":
            plain_text = " ".join(words)
            write_to_file(plain_text)
            words.clear()
            words.append(word)

        elif word == "Bot:":
            plain_text = " ".join(words)
            write_to_file(plain_text)
            words.clear()
            words.append(word)

        else:
            words.append(word)

    plain_text = " ".join(words)
    write_to_file(plain_text)

    return plain_text


def write_to_file(text):
    with open("Plain_text", "a") as file:
        file.write(text + "\n")
    file.close()


def main():
    open("Plain_text", "w")
    # Get key for translation of text
    key = read_code()

    # Gather all punctuation signs
    symbols = get_symbols()

    # Get the big hash and separate it
    hashed_data = read_file()
    hashed_letters = get_letters(hashed_data)

    # Decrypt the hashes
    letters = transform(hashed_letters, symbols)

    # Put the text back together
    plain_text = get_word(letters, key)


main()
