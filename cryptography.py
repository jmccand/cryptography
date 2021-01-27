import json

DEBUG = 0

def setup(full_words):
    wordsByLength = {}
    wordsByLetter = {}
    words = list(full_words.keys())
    words.sort()
    for word in words:
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
    while True:
        char = text.read(1)           
        if not char:  
            break
        else:
            if char.isalpha():
                word += char
            else:
                if word != '':
                    words.append(word)
                word = ''
    return words
    
def decrypt(wordsByLength, wordsByLetter, encrypted, decryption_index, decrypt_key, encrypt_key, decryptionType=False):
    
    indent = '  ' * decryption_index
    
    if DEBUG > 0:
        print(f'{indent}index {decryption_index} recursed again')
        print(f'{indent}encrypt key: {encrypt_key}\n{indent}decrypt key: {decrypt_key}')
    
    #base case
    if decryption_index == len(encrypted):
        return [decrypt_key]
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
        #filtering possible words based on requirements
        filtered_possible = []

        for word in possible_words:
            if DEBUG > 1:
                print(f'{indent}considering word {word} for encrypted word {encrypted_word}')
            requirementIndex = 0
            while requirementIndex < len(requirements):
                requirement = requirements[requirementIndex]
                if word[requirement[0]] != requirement[1]:
                    if DEBUG > 1:
                        print(f'{indent}  rejected')
                    break
                else:
                    requirementIndex += 1
            else:
                decrypt_key_copy = decrypt_key.copy()
                encrypt_key_copy = encrypt_key.copy()
                for charIndex, encrypted_char in enumerate(encrypted_word):
                    decrypted_char = word[charIndex]
                    if encrypted_char in decrypt_key_copy:
                        assert decrypt_key_copy[encrypted_char] == decrypted_char
                    elif decrypted_char in encrypt_key_copy and encrypted_char not in decrypt_key_copy:
                        if DEBUG > 1:
                            print(f'{indent}skipping word {word} because {decrypted_char} was already mapped to {encrypt_key_copy[decrypted_char]}')
                        break
                    else:
                        assert encrypted_char not in decrypt_key_copy
                        decrypt_key_copy[encrypted_char] = decrypted_char

                        assert decrypted_char not in encrypt_key_copy
                        encrypt_key_copy[decrypted_char] = encrypted_char
                else:
                    filtered_possible.append((word, decrypt_key_copy, encrypt_key_copy))
                    if DEBUG > 0:
                        print(f'{indent}keep word {word} for encrypted word {encrypted_word}')
                        
        if DEBUG > 0:
            print(f'{indent}length of possible words that survived filtering: {len(filtered_possible)}')
            
        solutions = []
        #recurse for each of the possible words
        for word, decrypt_key_copy, encrypt_key_copy in filtered_possible:
            if True or DEBUG > 0:
                print(f'{indent}recursing on word {word}')
            decryption = decrypt(wordsByLength, wordsByLetter, encrypted, decryption_index + 1, decrypt_key_copy, encrypt_key_copy)
            solutions.extend(decryption)

        return solutions

def showAnswers(solutions, full_encryption):
    if DEBUG > 0:
        print('solutions: ' + str(solutions))
    if solutions == []:
        print('No solutions found')
    else:
        for solution in solutions:
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
            print('SOLUTION:\n' + decrypted + '\n')
        
with open('words_dictionary.json') as f:
    words = json.load(f)

wordsByLength, wordsByLetter = setup(words)
#print('words by length:\n' + str(wordsByLength))
#print('\nwords by letter:\n' + str(wordsByLetter))

with open('encrypted.txt') as text:
    print('parsed:\n' + str(parse(text)))

with open('encrypted.txt') as text:
    solutions = decrypt(wordsByLength, wordsByLetter, parse(text), 0, {}, {})

with open('encrypted.txt') as text:
    showAnswers(solutions, text)
