import sys
import os

sys.path.append(os.path.abspath('../'))
import ahocorasick

def search_keywords_in_text(keywords:list, text):
    # Create an Aho-Corasick automaton
    A = ahocorasick.Automaton()

    # Add keywords to the automaton
    for index, keyword in enumerate(keywords):
        lowercase_keyword = keyword.lower()
        A.add_word(lowercase_keyword, (index, lowercase_keyword))

    # Finalize the automaton
    A.make_automaton()
    lower_text = text.lower()

    for word in lower_text.split():
        word_lower = word.lower()
        if word_lower in A:
            print(f"Found keyword: '{word_lower}'")
            return True  # Exit on first match
    print("No keywords found.")
    return False

def get_gene_list() -> list:
    genes = []
    with open('ref/genes.txt', 'r') as file:     
        genes = [line.strip() for line in file.readlines()]
    return genes
