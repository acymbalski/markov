#!/usr/bin/python3

import random

# for slow typing
import time, sys

# for book grabbing
import os

ORDER = 3
chain = {}


# used to try and guess the encoding of the source file
encoding_types = ["cp1252", "utf-8", "utf-16", "iso-8859-15", "cp437"]

def read_file(path):
    for enc in encoding_types:
        try:
            with open(path, 'r', encoding=enc) as f:
                txt = f.readlines()
                
            #print("Success decoding using {}...".format(enc))
            break
            
        except UnicodeDecodeError:
            #print("Error decoding using {}...".format(enc))
            pass
    return txt

def clean_text(txt):
    new_txt = []
    
    for line in txt:
        for word in line.split(' '):
    
            word = word.replace("\n", "")
            new_txt.append(word)
        
    return new_txt

def build_chain(txt):
    # count words
    for i in range(len(txt)):
    
        # if we don't have enough words yet to start building, move on, or if we're too close to the end and there's no next word
        if i < ORDER and i > len(txt):
            continue
        
        key = txt[i - ORDER:i]

        key = ' '.join(key)
        if key not in chain.keys():
            chain[key] = {}
            chain[key]["$Count"] = 0
        
        nextWord = txt[i]
        if nextWord not in chain[key].keys():
            chain[key][nextWord] = {}
            chain[key][nextWord]["$Count"] = 0
            chain[key][nextWord]["$Ratio"] = 0
        chain[key]["$Count"] += 1
        chain[key][nextWord]["$Count"] += 1
    
    # generate ratios
    for key in chain.keys():
        if key != "$Count":
            for nextWord in chain[key]:
                if nextWord != "$Count":
                    chain[key][nextWord]["$Ratio"] = chain[key][nextWord]["$Count"] / chain[key]["$Count"]
    

def generate(length=140):
    res = ""
    # first words are random, we need to start with some words of ORDER length to kick things off
    res = random.choice(list(chain.keys()))

    lastWords = res

    while len(res.split(' ')) < length:

        # get number in a uniform distribution to randomly select a word with weighting
        currentVal = random.uniform(0, 1.0)

        if lastWords in chain.keys():
            for key in chain[lastWords].keys():
            
                if key != "$Count":
                    if currentVal > chain[lastWords][key]["$Ratio"]:
                        currentVal -= chain[lastWords][key]["$Ratio"]
                    else:
                        currentWord = key
                        break
        else:
            # key not found, we probably grabbed the last word in a small sample document
            # the smart thing to do might be to back up until we DON'T run into this issue
            return res
                
        res += " {}".format(currentWord)
        
        # get the new last words of the generation
        lastWords = ' '.join(res.split(' ')[-ORDER:])
    
    return res



# type infinitely
# TODO: randomly pick a new book?

delay = 0.1

dir_path = os.path.dirname(os.path.realpath(__file__))

book_directory = os.path.join(dir_path, "books")

while True:
    # get random file
    filename = random.choice(os.listdir(book_directory))
    filePath = os.path.join(book_directory, filename)

    # print filename, order number
    ORDER = random.randint(1, 5)
    wordCount = random.randint(100, 250)
    

    w = read_file(filePath)
    w = clean_text(w)
    c = build_chain(w)
    
    generation = generate(wordCount).capitalize()

    if len(generation) > 80:
    
        print("Generating {} words from source book: \"{}\" with order of {}".format(len(generation.split(' ')), filename, ORDER))
        print("---")
        print()
        
        for c in generation:
            sys.stdout.write(c)
            sys.stdout.flush()
            
            if c in ['.', '!', '?']:
                time.sleep(delay * 3)
            if c in [';', ',', ')', ']']:
                time.sleep(delay * 2)
            else:
                time.sleep(delay)

        print("\n\n\n")
        time.sleep(2)

