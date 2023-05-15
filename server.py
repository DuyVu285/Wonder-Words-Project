import json
import random
import socket
import time

# Server configuration
HOST = 'localhost'
PORT = 12345
Buffersize = 1024

# Load words from JSON file
def loadJSON():
    with open('words_list.json') as f:
        words = json.load(f)
    return words

# Select words
def select_words(words):
    return random.choice(words)

# Generate the initial unrevealed word string
def generate_unrevealed_word(word):
    return ''.join(['-' if c != ' ' else ' ' for c in word])

# Handle player guesses
def handle_guess(guess, word, unrevealed_word):
    if guess in word:
        for i, c in enumerate(word):
            if c == guess:
                unrevealed_word = unrevealed_word[:i] + guess + unrevealed_word[i+1:]
        return unrevealed_word, True
    else:
        return unrevealed_word, False
    

UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

UDPServerSocket.bind((localIP, localPort))
print("UDP server up and listening")

while True:
    bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)

    message = bytesAddressPair[0]

    address = bytesAddressPair[1]

    print(message)
    clientMsg = "Message from Client:{}".format(message)
    clientIP = "Client IP Address:{}".format(address)

    print(clientMsg)
    print(clientIP)

    UDPServerSocket.sendto(bytesToSend, address)

