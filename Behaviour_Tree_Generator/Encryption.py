import hashlib

data = []
size = []


def read_text():

    with open("Conversation", "r") as file:
        for line in file:
            for word in line.split():    # Read word by word
                data.append(word)   # Collect words
                size.append(len(word))   # And their length
    file.close()


def shuffle(hashed):
    hash_list = []
    temp = []
    new_hash = ""

    max_len = len(hashed)-6
    for char in range(0, max_len):
        hash_list.append(hashed[char])  # Transform the word into a char array

    char = max_len
    for n in range(0, 6):
        temp.append(hashed[char+n])   # Separate the last 6 symbols

    for char in range(0, len(hash_list)):  # Shuffle the last 6 symbols with the rest
        new_hash += hash_list[char]

        if len(new_hash) == 8:     # Key
            for n in range(0, 2):
                new_hash += temp[0]
                temp.remove(temp[0])

        elif len(new_hash) == 14:
            for n in range(0, 2):
                new_hash += temp[0]
                temp.remove(temp[0])

        elif len(new_hash) == 22:
            for n in range(0, 2):
                new_hash += temp[0]
                temp.remove(temp[0])

    return new_hash


def encrypt():
    hash_list = []
    num_words = len(data)
    for num in range(0, num_words):
        word = data[num]   # Get every word in the file

        for char in range(0, len(word)):   # Encrypt each char
            to_hash = word[char]
            hashed = hashlib.sha256(str.encode(to_hash)).hexdigest()
            shuffled = shuffle(hashed)    # Shuffle before saving!
            hash_list.append(shuffled)

    return hash_list


def write_to_file(hashed):
    with open("Hash", "a") as file:   # Write hash
        file.write(hashed)
        file.close()


def write_code():                     # Write reading key
    with open("Code", "w") as file:
        for i in range(0, len(size)):
            file.write(str(size[i]) + "\n")
    file.close()


def main():
    open("Code", "w")  # Clean the files
    open("Hash", "w")

    # Get conversation
    read_text()
    # Create key for interpretation
    write_code()

    # Encrypt the text
    to_write = encrypt()
    for i in range(0, len(to_write)):   # Create a big hash
        write_to_file(to_write[i])      # Write it to a file
    open("Conversation", "w")


#main()
