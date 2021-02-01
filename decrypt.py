import json
import sys
import wordfreq
import time
import string

# TODO
#   - run on dad's fastest computer!
#   - allow inputting a "starting guess" from the user, e.g. "python is the last word"
#   - use inverted letter index to more quickly filter words
#   - use multiprocess
#   - print partial decode so far during DEBUG > 0
#   - maybe print sum of word freq for each solution?  might help us spot most likely solution?  we could print all solutions ranked by that in the "end"
#   - could we print some kind of overall %tg done somehow?  e.g. for each solution we could print what %tg through the word list each word was?
#   - maybe trim very low frequency words, not just 0 frequency?
#   - take "typical" letter frequencies into account, law of large numbers?
#   - print out letter frequencies in the encoded text
#   - don't decode left to right, go from longest words to shortest
#   - optimize function can be recursive

DEBUG = 0

def setup(full_words):
    wordsByLength = {}
    wordsByLetter = {}
    words = list(full_words.keys())
    words_with_frequency = []
    for word in words:
        words_with_frequency.append((word, wordfreq.word_frequency(word, 'en')))

    words_with_frequency.sort(key=lambda x: -x[1])

    first_50 = words_with_frequency[0: 50]
    if DEBUG > 0:
        for tuple_pair in first_50:
            print(tuple_pair[0])

    sorted_words = [x[0] for x in words_with_frequency]
#    sorted_words = [x[0] for x in words_with_frequency if x[1] > 0]
    print(f'length of words with old dictionary: {len(full_words)}, length of words removed zeroes: {len(sorted_words)}')
    
    for word in sorted_words:
        length = len(word)
        if length in wordsByLength:
            wordsByLength[length].append(word)
        else:
            wordsByLength[length] = [word]
        for char in word:
            if char in wordsByLetter:
                wordsByLetter[char].append(word)
            else:
                wordsByLetter[char] = [word]
    return wordsByLength, wordsByLetter

def parse(text):
    word = ''
    words = []
    for char in text:
        if char.isalpha():
            word += char
        else:
            if word != '':
                words.append(word)
            word = ''
    return words

def optimize(word_list):
    seen = set()
    word_priority = []
    while True:
        if DEBUG > 1:
            print(f'word priority: {word_priority}')
            print(f'seen: {seen}')
        word_scores = []
        for word in word_list:
            distinct_letters = set()
            for char in word:
                if char not in seen:
                    distinct_letters.add(char)
            word_scores.append((word, len(distinct_letters)))
        word_scores.sort(key=lambda x: -x[1])
        if word_scores[0][1] == 0:
            break
        else:
            word_priority.append(word_scores[0][0])
            for char in word_scores[0][0]:
                seen.add(char)
    
    return word_priority
    
def decrypt(wordsByLength, wordsByLetter, encrypted, decryption_index, decrypt_key, encrypt_key):

    global solutionCount
    
    indent = '  ' * decryption_index
    
    if DEBUG > 0:
        print(f'{indent}index {decryption_index} recursed again')
        print(f'{indent}encrypt key: {encrypt_key}\n{indent}decrypt key: {decrypt_key}')

    #base case
    if decryption_index == len(encrypted):
        solutionCount += 1
        showAnswer(decrypt_key)
    else:
        encrypted_word = encrypted[decryption_index]
        possible_words = wordsByLength[len(encrypted_word)]
        requirements = []

        #setting requirements for possible words
        for index, char in enumerate(encrypted_word):
            if char in decrypt_key:
                requirements.append((index, decrypt_key[char]))

        if DEBUG > 0:
            print(f'{indent}requirements: {requirements}')

        for word in possible_words:
            if DEBUG > 1:
                print(f'{indent}considering word {word} for encrypted word {encrypted_word}')
            for index, letter in requirements:
                if word[index] != letter:
                    if DEBUG > 1:
                        print(f'{indent}  rejected')
                    break
            else:
                added = []
                for charIndex, encrypted_char in enumerate(encrypted_word):
                    decrypted_char = word[charIndex]
                    if encrypted_char in decrypt_key:
                        if decrypt_key[encrypted_char] != decrypted_char:
                            if DEBUG > 1:
                                print(f'{indent}skipping word {word} because {encrypted_char} was already mapped to {decrypt_key[encrypted_char]}')
                            break
                    elif decrypted_char in encrypt_key:
                        if encrypt_key[decrypted_char] != encrypted_char:
                            if DEBUG > 1:
                                print(f'{indent}skipping word {word} because {decrypted_char} was already mapped to {encrypt_key[decrypted_char]}')
                            break
                    else:
                        assert encrypted_char not in decrypt_key, f'encrypted_char {encrypted_char} already in decrypt_key {decrypt_key}'
                        decrypt_key[encrypted_char] = decrypted_char

                        assert decrypted_char not in encrypt_key, f'decrypted_char {decrypted_char} already in encrypt_key {encrypt_key}'
                        encrypt_key[decrypted_char] = encrypted_char
                        added.append(encrypted_char)
                else:
                    if DEBUG > 0:
                        print(f'{indent}{decryption_index}: recursing on word {word}')
                    #recurse on possible word:
                    decrypt(wordsByLength, wordsByLetter, encrypted, decryption_index + 1, decrypt_key, encrypt_key)

                #clean up added mappings:
                for encrypted_char in added:
                    decrypted_char = decrypt_key[encrypted_char]
                    del decrypt_key[encrypted_char]
                    del encrypt_key[decrypted_char]

def decrypt_caesar(wordsByLength, wordsByLetter, parsed_list, start_decrypt_key, start_encrypt_key):
    global solutionCount
    for shift in range(1, 26):
        temp_decrypt_key, temp_encrypt_key = build_caesar(shift)
        # print(f'temporary decrypt key for shift {shift}: {temp_decrypt_key}')
        decrypt(wordsByLength, wordsByLetter, parsed_list, 0, temp_decrypt_key, temp_encrypt_key)
        
def build_caesar(shift):
    decrypt_key = {}
    encrypt_key = {}
    for index, char in enumerate(string.ascii_uppercase):
        shifted_char = string.ascii_lowercase[(index + shift) % 26]
        decrypt_key[char] = shifted_char
        encrypt_key[shifted_char] = char
    return decrypt_key, encrypt_key
                    
def showAnswer(solution):
    with open(INPUT_FILE) as full_encryption:
        if DEBUG > 0:
            print('solutions: ' + str(solution))
        decrypted = ''
        while True:
            char = full_encryption.read(1)
            if not char:
                break
            else:
                if char in solution:
                    decrypted += solution[char]
                else:
                    decrypted += char
        print(f'{time.time() - startTime:.2f}s: SOLUTION {solutionCount}: {decrypted.strip()}')
        if DEBUG > 2:
            for index, word in enumerate(parse(decrypted)):
                print(f'{index}: {word}')

def main():
    global startTime
    global solutionCount
    global INPUT_FILE

    CAESAR_MODE = '-caesar' in sys.argv
    if CAESAR_MODE:
        sys.argv.remove('-caesar')

    if len(sys.argv) > 1:
        INPUT_FILE = sys.argv[1]
    else:
        INPUT_FILE = 'encrypted.txt'

    # how many solutions we've found so far
    solutionCount = 0

    print(f'Trying to decrypt file "{INPUT_FILE}"')
    if CAESAR_MODE:
        print('CAESAR MODE')

    with open('words_dictionary.json') as f:
        words = json.load(f)

    wordsByLength, wordsByLetter = setup(words)
    #print('words by length:\n' + str(wordsByLength))
    #print('\nwords by letter:\n' + str(wordsByLetter))

    startTime = time.time()

    with open(INPUT_FILE) as text:
        parsed_list = parse(text.read())
        start_decrypt_key = {}
        start_encrypt_key = {}
        if len(sys.argv) > 3:
            INDEX, WORD = sys.argv[2:4]
            INDEX = int(INDEX)
            known_encrypted_word = parsed_list[INDEX]
            for index, char in enumerate(WORD):
                start_decrypt_key[known_encrypted_word[index]] = char
                start_encrypt_key[char] = known_encrypted_word[index]
        print(f'start decrypt: {start_decrypt_key}, start encrypt: {start_encrypt_key}')

        print(f'parsed: {len(parsed_list)}')
        for index, word in enumerate(parsed_list):
            print(f'{index}: {word}')

        parsed_list.sort(key=lambda x: -len(x))
        print(f'sorted: {len(parsed_list)} words\n{parsed_list}')

        optimized_list = optimize(parsed_list)
        print(f'optimized: {len(optimized_list)} (removed {len(parsed_list) - len(optimized_list)})  words\n{optimized_list}')


        if CAESAR_MODE:
            decrypt_caesar(wordsByLength, wordsByLetter, optimized_list, start_decrypt_key, start_encrypt_key)

        else:
            decrypt(wordsByLength, wordsByLetter, optimized_list, 0, start_decrypt_key, start_encrypt_key)

if __name__ == '__main__':
    main()
