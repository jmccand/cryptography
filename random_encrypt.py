import random
import string
import json

def main():
    '''
    Simple tool to to create a random letter cipher and then encrypt text from
    local file "input.txt" and write it to "output.txt".  It also writes
    decrypt_key.json and encrypt_key.json.
    '''

    letters = list(string.ascii_uppercase)

    random.shuffle(letters)

    encrypt_key = {}
    decrypt_key = {}

    for i, letter in enumerate(string.ascii_lowercase):
        encrypt_key[letter] = letters[i]
        decrypt_key[letters[i]] = letter
    json.dump(decrypt_key, open('decrypt_key.json', 'w'))
    json.dump(encrypt_key, open('encrypt_key.json', 'w'))

    with open('input.txt', 'r') as f_in, open('output.txt', 'w') as f_out:
        text = f_in.read()
        encrypted_text_list = []
        for letter in text:
            # this way space, punctuation just carry through unchanged:
            encrypted_text_list.append(encrypt_key.get(letter, letter))
        f_out.write(''.join(encrypted_text_list))

if __name__ == '__main__':
    main()
