test_sentence = 'The quick brown fox jumps (leaps) 5 feet over the lazy dog at 10% his running speed.'
test_list = ['quick', 'fox', 'the', 'dog', 'speed']

import string
import re

def term_sentence_position(sentence: str, term_list: list):
    
    sentence = re.sub('[^a-zA-Z0-9\s]', '', sentence)
    sentence = re.sub('[0-9]', '', sentence)
    sentence = sentence.lower().split(' ')
    sentence = [word for word in sentence if word != '']
    output = {}
    
    for term in term_list:
        if term in sentence:
            output[term] = []
        for i, word in enumerate(sentence):
            if term == word:
                output[term].append(i)
                
    return output

term_sentence_position(test_sentence, test_list)