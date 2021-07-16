'''
The implemented Eliza strategies:
1) Ask questions of the form “Do you like to x” where x is the 
infinitive form of a verb in the user’s early input
2) Ask questions of the form “You said that ..x…? Tell me more!” 
where x is the rephrased input from the user.
3) Ask questions of the form “Why is ..x..?” where x is either a 
combination of object and adjective or subject and adjective 
or “Why ..prep.. the ..noun..”
'''

from dependency_parsing import *
import random

def swap(string, dep):
    if string.lower() == "i" or string.lower() == "me":
        return "you"
    elif string.lower() == "my":
        return "your"
    elif string.lower() == "myself":
        return "yourself"
    elif string.lower() == "you":
        if dep == "nsubj": # might have to add more
            return "i"
        else:
            return "me"
    elif string.lower() == "your":
        return "my"
    elif string.lower() == "yourself":
        return "myself"
    elif string.lower() == "yours":
        return "mine"
    else:
        return string


first_person = {"i", "me", "my", "myself", "mine"}
second_person = {"you", "your", "yourself", "yours"}
def swap_doc_first_to_second(doc):
    string_list = []
    for token in doc:
        new_text = swap(token.text, token.dep_)
        string_list.append(new_text)

    return string_list


def swap_dict_first_to_second(chunk_dict):
    """
    Returns a dictionary of spacy object that switched first person noun(s)
    to second person noun(s).

    Used on chunks that get parsed from the functions in dependency_parsing.py
    """
    res_dict = {}
    for key in chunk_dict.keys():
        token = chunk_dict[key]
        new_text = swap(token.text, token.dep_)
        res_dict[key] = new_text

    return res_dict
    

def ask_do_you_like_to(doc):
    """
    Ask questions of the form “You said that ..x…? Tell me more!” 
    where x is the rephrased input from the user.
    """
    chunk = find_verb_chunk(doc)
    if chunk != None:
        verb = chunk["verb"].lemma_
        obj = chunk["object"]

        if verb == "like": #avoids "Do you like to like..."
            return None

        return "Do you like to {} {}?".format(verb, obj)

    chunk = find_subj_verb_chunk(doc)
    if chunk != None:
        verb = chunk["verb"].lemma_

        if verb == "like": #avoids "Do you like to like"
            return None

        return "Do you like to {}?".format(verb)
        
    return None
    

def rephrase_question(doc):
    '''
    Rephrases the sentence into 
        You said that...

    It tries to parse subject, verb, preposition, and object (to get most info)
    first before it tries to parse only subject, verb, and object.

    '''
    chunk = find_subj_verb_prep_obj_chunk(doc)
    if chunk != None:
        second_person_chunk = swap_dict_first_to_second(chunk)

        subj = second_person_chunk["subject"]
        verb = second_person_chunk["verb"]
        prep = second_person_chunk["preposotion"]
        obj = second_person_chunk["object"]
        question = "You said that {} {} {} the {}? Tell me more!".format(subj, verb, prep, obj)
        return question

    chunk = find_verb_chunk(doc)
    if chunk != None:
        second_person_chunk = swap_dict_first_to_second(chunk)

        subj = second_person_chunk["subject"]
        verb = second_person_chunk["verb"]
        obj = second_person_chunk["object"]
        question = "You said that {} {} {}? Tell me more!".format(subj, verb, obj)
        return question

    return None


def ask_why(doc):
    """
    Ask questions of the form “Why is ..x..?” where x is either a 
    combination of object and adjective or subject and adjective 
    or “Why ..prep.. the ..noun..”
    """
    chunk = find_subj_chunk(doc)
    if chunk != None and chunk["adjective"] != None:
        subj = chunk["subject"]
        adj = chunk["adjective"]
        respond = "Why is {} {}?".format(subj, adj)
        return respond
    
    chunk = find_obj_chunk(doc)
    if chunk != None and chunk["adjective"] != None:
        subj = chunk["objective"]
        adj = chunk["adjective"]
        respond = "Why is {} {}?".format(subj, adj)
        return respond

    # I had similar experience in high school --> why in high school?
    chunk = find_prep_chunk(doc)
    if chunk != None:
        subj = chunk["full_subject"]
        prep = chunk["prep"]
        respond = "Why {} the {}?".format(prep, subj)
        return respond

    return None
    

def try_all_eliza_transformations(doc):
    """
    Try to do eliza transformation for all the functions and add the transformed string to the
    responses list
    """
    responses = []
    question = ask_do_you_like_to(doc)
    if question:
        responses.append(question)

    question = rephrase_question(doc)
    if question:
        responses.append(question)

    question = ask_why(doc)
    if question:
        responses.append(question)

    return responses


def main():
    """
    Main function for testing
    """
    test_string = "I walked in the Arb sometimes."
    nlp = spacy.load("en_core_web_sm")  
    doc = nlp(test_string)
    ques = rephrase_question(doc)


if __name__ == "__main__":
    main()