'''
////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////
///////                                                                                                  ///////
///////                                                                                                  ///////
///////                                                                                                  ///////
///////       KK       KK       OOOOO        FFFFFFFFFFF   FFFFFFFFFFF   EEEEEEEEEEE   EEEEEEEEEEE       ///////
///////       KK     KK       O       O      FF            FF            EE            EE                ///////
///////       KK   KK       OO         OO    FF            FF            EE            EE                ///////
///////       KK KK        OO           OO   FF            FF            EE            EE                ///////
///////       KKKK         OO           OO   FFFFFFFFFFF   FFFFFFFFFFF   EEEEEEEEEEE   EEEEEEEEEEE       ///////
///////       KK KK        OO           OO   FF            FF            EE            EE                ///////
///////       KK   KK       OO         OO    FF            FF            EE            EE                ///////
///////       KK     KK       O       O      FF            FF            EE            EE                ///////
///////       KK       KK       OOOOO        FF            FF            EEEEEEEEEEE   EEEEEEEEEEE       ///////
///////                                                                                                  ///////
///////                                                                                                  ///////
///////                                                                                                  ///////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////

koffee.py
the main file for the chatbot's tour of Carleton College

@author: Yuting, PJ, and Minh
@date: 05/14/2021
'''

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ[f'TRANSFORMERS_VERBOSITY'] = 'critical'

import tensorflow as tf
import logging
tf.get_logger().setLevel(logging.ERROR) # surpresses error when calling dialogtag_model.predict_tag

from dialog_tag import DialogTag
from profanity import profanity
from textblob import TextBlob
from dependency_parsing import *
from markov_run import *
from building import *
from eliza import *
import random
import spacy
import time
import re


def print_text_art():
    print("\n")
    print("//////////////////////////////////////////////////////////////////////////////////////////////////////")
    print("//////////////////////////////////////////////////////////////////////////////////////////////////////")
    print("////                                                                                              ////")
    print("////                                                                                              ////")
    print("////                                                                                              ////")
    print("////     KK       KK       OOOOO        FFFFFFFFFFF   FFFFFFFFFFF   EEEEEEEEEEE   EEEEEEEEEEE     ////")
    print("////     KK     KK       O       O      FF            FF            EE            EE              ////")
    print("////     KK   KK       OO         OO    FF            FF            EE            EE              ////")
    print("////     KK KK        OO           OO   FF            FF            EE            EE              ////")
    print("////     KKKK         OO           OO   FFFFFFFFFFF   FFFFFFFFFFF   EEEEEEEEEEE   EEEEEEEEEEE     ////")
    print("////     KK KK        OO           OO   FF            FF            EE            EE              ////")
    print("////     KK   KK       OO         OO    FF            FF            EE            EE              ////")
    print("////     KK     KK       O       O      FF            FF            EE            EE              ////")
    print("////     KK       KK       OOOOO        FF            FF            EEEEEEEEEEE   EEEEEEEEEEE     ////")
    print("////                                                                                              ////")
    print("////                                                                                              ////")
    print("////                                                                                              ////")
    print("//////////////////////////////////////////////////////////////////////////////////////////////////////")
    print("//////////////////////////////////////////////////////////////////////////////////////////////////////")
    print("\n")


# initialize models
koffee_grammar = Grammar('./koffee_response/koffee.json')
dialogtag_model = DialogTag('distilbert-base-uncased')
SLM_model = train_markov("./texts/markov_text.txt")
nlp = spacy.load("en_core_web_sm")

building_names = ["anderson", "cmc", "libe", "olin", "sayles", "weitz"]
majors_building_dict = {
    "psychology": "olin",
    "physics": "olin",
    "astronomy": "olin",
    "computer science": "olin",

    "maths": "cmc",
    "statistics": "cmc",

    "chemistry": "anderson",
    "geology": "anderson",
    "chemistry": "anderson",

    "cinema and media studies": "weitz",
    "music": "weitz",
    "dance": "weitz",

    "other": "",
    "": ""
}

# run-time variables
name = ""
major = ""
start_building = ""
previous_building = ""
current_building = ""
is_intro = True
told_funfact = False


def koffee_print(string):
    '''
    Prints koffee's responses
    '''
    time.sleep(0.5)
    string_list = string.split(" ")
    charCount = 0

    print("Koffee:", end=" ")
    for i in range(len(string_list)):
        if charCount > 70: # breaks line ~ every 70 characters
            print("\n" + (" "*8), end="")
            charCount = 0
            
        print(string_list[i], end=" ")
        charCount += len(string_list[i])
    print()
    time.sleep(0.5)


def user_print():
    '''
    Prints UI to prompt user's imputs
    '''
    return Response(input("You:" + (" "*4)))


def remove_symbol_from_string(string):
    return re.sub(r'[^\w]', '', string)


def cap_first_character(string):
    if string == "":
        return ""

    if string.lower() == "cmc".lower():
        return "CMC"

    return string[0].upper() + string[1:]
     

# keyphraase variables
given_winter_fact = False
given_polar_vortex_fact = False
given_spring_fact = False
winter_keyphrase = {"winter", "cold", "snow", "ski", "skate", "ice"}
polar_vortex_keyphrase = {"polar", "vortex", "steven", "poskanzer", "steve"}
spring_keyphrase = {"spring", "music", "tradition", "beautiful", "tennis"}

def check_keyphrase(response_string):
    """
    Generates fun facts if the given string contains any keyphrase. Will generate at most one funfact per call
    """
    global given_winter_fact 
    global given_polar_vortex_fact 
    global given_spring_fact 
    global winter_keyphrase 
    global polar_vortex_keyphrase 
    global spring_keyphrase 
    global told_funfact 

    string_list = response_string.lower().split(" ")
    for word in string_list:
        word = remove_symbol_from_string(word) # removes fullstop, comma, colon, etc

        if not given_winter_fact and word in winter_keyphrase:
            koffee_print(koffee_grammar.generate("funFactIntro") + " {}. ".format(word.lower()) + koffee_grammar.generate("winterFunFact"))
            given_winter_fact = True
            told_funfact = True
            time.sleep(1)
            return

        elif not given_polar_vortex_fact and word in polar_vortex_keyphrase:
            koffee_print(koffee_grammar.generate("funFactIntro") + " {}. ".format(word.lower()) + koffee_grammar.generate("polarVortexFunFact"))
            given_polar_vortex_fact = True
            told_funfact = True
            time.sleep(1)
            return

        elif not given_spring_fact and word in spring_keyphrase:
            koffee_print(koffee_grammar.generate("funFactIntro") + " {}. ".format(word.lower()) + koffee_grammar.generate("sprintFunFact"))
            given_spring_fact = True
            told_funfact = True
            time.sleep(1)
            return
            

class Response:
    """
    Wrapper class for user's response. The class contains everything that is required for our NLU module.
    """
    def __init__(self, response_string):
        global is_intro

        self.response_string = response_string
        self.sentiment = TextBlob(response_string).sentiment
        self.tag = dialogtag_model.predict_tag(response_string)

        doc = nlp(response_string)

        self.eliza_transformation = try_all_eliza_transformations(doc) # list of eliza transformed string(if there is any)
        self.is_eliza = False if len(self.eliza_transformation) == 0 else True

        self.ner = [(ent.text, ent.label_) for ent in doc.ents]

        is_profanity = profanity.contains_profanity(response_string)
        if (is_profanity):
            koffee_print(koffee_grammar.generate("profanityResponse"))

        # only checks keyphrase when the bot is not doing an intro
        if not is_intro:
            check_keyphrase(response_string)


def print_response_class(response):
    """
    Helper function to print all the variables in the Response class.
    """
    string_response_class = "\nstring: {}\nsentiment: {}\ntag: {}\neliza_transformation: {}\nis_eliza: {}\nner: {}\nkeyphrase: {}\nis_profanity: {}\n".format(
        response.response_string, response.sentiment, response.tag, response.eliza_transformation, response.is_eliza, response.ner, response.keyphrase, response.is_profanity
    )
    print()
    print("Printing Response Class")
    print(string_response_class)
    print()


def initialize_buiildings():
    """
    Initializes Building classes for all the buildings and returns them in form of a dictionary.
    """
    return {
        "libe": Building('./building_grammars/libe.json', "libe"),
        "olin": Building('./building_grammars/olin.json', "olin"),
        "weitz": Building('./building_grammars/weitz.json', "weitz"),
        "cmc": Building('./building_grammars/cmc.json', "cmc"),
        "anderson": Building('./building_grammars/anderson.json', "anderson"),
        "sayles": Building('./building_grammars/sayles.json', "sayles")
    }


# major phrases varaibles
cs_phrases = {"cs", "computer", "programming", "coding", "ai", "nlp", "blockchain"}
psychology_phrases = {"psyc", "psychology", "brain", "brains", "thoughts"}
physics_phrases = {"physics", "quantum", "gravity", "matters"}
astronomy_phrases = {"astronomy", "universe"}
maths_phrases = {"math", "maths", "mathematics", "mathematic", "numbers"}
statistics_phrases = {"stat", "statistic", "statisitcs", "data"}
biology_phrases = {"bio", "biology", "med", "premed", "medicine"}
chemistry_phrases = {"chem", "chemistry"}
cams_phrases = {"cams", "cinema", "media", "film", "production", "movie", "movies", "films"}
music_phrases = {"music", "musics", "composition", "singing", "piano"}
dance_phrases = {"dance", "kpop", "ballet", "hiphop"}

def update_major_on_string(response_string):
    global major
    global start_building

    # no need to detect major if a major is already picked up
    if major != "" and major != "other":
        return

    response_list = response_string.lower().split(" ")

    # check all the words in the response string
    for word in response_list:
        word = remove_symbol_from_string(word) # removes fullstop, comma, colon, etc

        if word in cs_phrases:
            major = "Computer Science"
            start_building = "olin"
            return
        elif word in psychology_phrases:
            major = "Psychology"
            start_building = "olin"   
            return
        elif word in physics_phrases:
            major = "Physics"
            start_building = "olin"   
            return
        elif word in astronomy_phrases:
            major = "Astronomy"
            start_building = "olin"   
            return
        elif word in maths_phrases:
            major = "Maths"
            start_building = "cmc" 
            return
        elif word in statistics_phrases:
            major = "Statistics"
            start_building = "cmc" 
            return      
        elif word in biology_phrases:
            major = "Biology"
            start_building = "anderson"
            return
        elif word in chemistry_phrases:
            major = "Chemistry"
            start_building = "anderson"
            return
        elif word in cams_phrases:
            major = "Cinema and Media Studies"
            start_building = "weitz"
            return
        elif word in music_phrases:
            major = "Music"
            start_building = "weitz"
            return
        elif word in dance_phrases:
            major = "Dance"
            start_building = "weitz"
            return

    # defaults starting_building to Sayles if no major is picked up
    major = "other"
    start_building = "sayles"


def generate_sentiment(response):
    """
    Prints response based on the sentiment of the given response.
    """
    if response.sentiment.polarity < -0.4:
        koffee_print(koffee_grammar.generate("veryNegative"))

    elif response.sentiment.polarity > 0.4:
        koffee_print(koffee_grammar.generate("veryPositive"))

    else:
        if response.sentiment.subjectivity < 0.2:
            koffee_print(koffee_grammar.generate("veryObjective"))
        elif response.sentiment.subjectivity > 0.8:
            koffee_print(koffee_grammar.generate("verySubjective"))
        else:
            koffee_print(koffee_grammar.generate("neturalResponse"))


def generate_eliza_or_sentiment(response):
    """
    Prints eliza transformed text. If the response can not be eliza transformaed, call 
    generate_sentiment on the response instead
    """
    if response.is_eliza:
        koffee_print(random.choice(response.eliza_transformation))
        follow_up_response = user_print()
        update_major_on_string(follow_up_response.response_string)
        
        # continue the conversation if it can be transformed to eliza
        max_conversation = random.randrange(3) #at most 3 times
        count = 0
        while count < max_conversation and follow_up_response.is_eliza:
            koffee_print(random.choice(follow_up_response.eliza_transformation))
            follow_up_response = user_print()
            update_major_on_string(follow_up_response.response_string)
            count += 1

        generate_sentiment(follow_up_response)

    else:
        generate_sentiment(response)


# questions for small talk
sentiment_questions = [
    "How did you get here? Was it a long trip?",
    "How do you like the weather here?",
    "How do you feel about snow?",
    "How do you feel about living in a dorm?",
    "How are you feeling so far?",
    "How do you feel about being away from home?"
]
    
eliza_questions = [
    "What do you enjoy doing in your free time?",
    "What's your favorite food?",
    "What's your plan for this up coming summer?",
    "How did you hear abour Carleton?",
    "Do you think Cereal is a soup?",
    "Is hot dog a sandwich?",
    "What do you normally do in your weekends?"
]

yesno_questions = [
    "Do you like our down town, Northfiled?",
    "Do you want to go to graduate school?",
    "Do you plan to work in an academic sector?"
]

yes_tags = ["Yes answers", "Affirmative non-yes answers"]
no_tags = ["No answers", "Negative non-no answers"]
small_talk_questions = [("SENTIMENT", sentiment_questions), ("ELIZA", eliza_questions), ("YESNO", yesno_questions)]

def small_talk():
    global small_talk_questions
    global yes_tags
    global no_tags
    # removes question list that is empty
    small_talk_questions = [question for question in small_talk_questions if len(question[1]) > 0]
    qustion_tuple = random.choice(small_talk_questions)
    question_header = qustion_tuple[0]
    question_string = random.choice(qustion_tuple[1])

    # talk about a markov_generated quote ~ every three small talks
    if random.choice([1,2,3]) == 1:
        s = "Do you know that the president said \"" + (SLM_model.generate(50)) + "\" I thought that was cool."
        koffee_print(s)

    # removes question from small_talk_questions
    for tup in small_talk_questions:
        if tup[0] == question_header:
            tup[1].remove(question_string)

    koffee_print(question_string)
    response = user_print()
    update_major_on_string(response.response_string) # keeps checking what major might the user be intersed in

    if question_header == "ELIZA":
        generate_eliza_or_sentiment(response)

    elif question_header == "SENTIMENT":
        generate_sentiment(response)

    elif question_header == "YESNO":
        if response.tag in yes_tags or response.tag in no_tags:
            koffee_print(koffee_grammar.generate("veryPositive"))

        else:
            generate_sentiment(response)


user_question_keywords = ["workload", "trisemester", "career", "core curriculum", "internet", "food"]

def user_question(response_string):
    """
    Prints a response to the user's "question" if the response string contains any string in user_question_keywords
    """
    global user_question_keywords

    for keyword in user_question_keywords:
        if keyword in response_string.lower():
            koffee_print(koffee_grammar.generate(keyword))
            user_question_keywords.remove(keyword)
            return

    koffee_print("Woo that's a good question but I am not sure about the answer. Feel free to ask the admission office and I believe they know the answer!")


def introduction_conversation():
    """
    Does a conversation with the user and tries to get the user's name and prospective major. The first building that
    it will bring the user to will be determined by the response to the perspective major. If nothing is picked up,
    it will bring the user to Sayles.
    """
    global name
    global major
    global start_building
    global current_building
    global is_intro

    koffee_print("Hi I'm Koffee. I'm your tour-guide today. Welcome to Carleton College! What's your name?")
    response = user_print()
    for ent in response.ner:
        if ent[1] == "PERSON":
            name = ent[0]

    if name == "":
        koffee_print("So sorry, but I didn't catch your name. What is your name again? Perhaps give me your full name?")
        name_response = user_print()

        for ent in name_response.ner:
            if ent[1] == "PERSON":
                name = ent[0]

        if name == "":
            name = "friend"

    koffee_print("Nice to meet you {}!".format(name))

    koffee_print("What's your prospective major? or what are the things you enjoy doing?")
    major_response = user_print()

    # match the given major with the first building that the tour will visit    
    response_string = major_response.response_string
    update_major_on_string(response_string)

    current_building = start_building

    if major == "other":
        koffee_print("You will be encouraged to try many things out at Carleton!")
        time.sleep(0.4)
        koffee_print("The whole tour will take around 2 to 4 minutes. I will take you to three very cool buildings.")
        time.sleep(0.4)
        koffee_print("Please follow me, our first stop will be at {}".format(cap_first_character(start_building)))
    else:
        koffee_print("Awesome! {} sounds like a good fit for you.".format(major))
        time.sleep(0.4)
        koffee_print("The whole tour will take around 2 to 4 minutes. I will take you to three very cool buildings.")
        time.sleep(0.4)
        koffee_print("Let's start our tour at {}, follow me!".format(cap_first_character(start_building)))
    
    is_intro = False


def is_no_response(response):
    global no_tags

    if "no" in response.response_string.lower():
        return True

    for ent in response.ner:
        if ent[1] in no_tags:
            return True
    
    return False


def visit_building(building):
    """
    Generates text from the contex-free-gramar of the given building object. It will generate introduction and 
    features non terminal first. After that, it will randomly genearte one more nonterminal from what are left 
    in building_components.

    Parameter:
        Building object
    """
    global major
    global told_funfact

    if building.name == majors_building_dict[major.lower()]:
        koffee_print("This building may interest you! It is a building for {}.".format(cap_first_character(major)))
        time.sleep(0.5)

    # use start_building, which is filled in introduction_conversation()
    building_components = ["majors", "offices", "funFact"]
    koffee_print(building.generate_fact("introduction"))
    
    time.sleep(1.1)
    koffee_print(building.generate_fact("features"))
    time.sleep(1.1)

    another_component = random.choice(building_components)
    if another_component.lower() == "funfact":
        told_funfact = True
        koffee_print(koffee_grammar.generate("funFactBuildingIntro") + " {}, ".format(cap_first_character(building.name)) + building.generate_fact("funFact"))
    else:
        koffee_print(building.generate_fact(another_component))

    koffee_print("Any Question?")
    response = user_print()

    if is_no_response(response):
        koffee_print(koffee_grammar.generate("getGoing"))
    else:
        user_question(response.response_string)


told_baldSpot = False
told_careerCenter = False
told_chapel = False

def transition():
    """
    Prints updates on where the user is heading. Also prints facts about bald spot, career center, or chapel based on
    the route that the user is walking on.
    """
    global previous_building
    global current_building
    global told_baldSpot
    global told_careerCenter
    global told_chapel
    
    previous_lower = previous_building.lower()
    current_lower = current_building.lower()

    cap_current = cap_first_character(current_building)
    cap_previous = cap_first_character(previous_building)

    time.sleep(0.5)
    if previous_lower == "":
        print("...Walking towards {}...".format(cap_current))
    else:
        print("...Walking from {} to {}...".format(cap_previous, cap_current))

    time.sleep(0.5)
    small_talk()
    time.sleep(0.5)
    # if walk from sayles or towards sayles or towards weitz(but not from olin or anderson)
    if not told_baldSpot and (previous_lower == "sayles" or (current_lower == "sayles" and previous_lower != "") or 
        (current_lower == "weitz" and (previous_lower != "olin" or previous_lower != "anderson"))):

        koffee_print(koffee_grammar.generate("baldSpotStory"))
        told_baldSpot = True

    elif not told_careerCenter and previous_lower == "weitz" and (current_lower == "sayles" or 
        current_lower == "libe" or current_lower == "cmc"):

        koffee_print(koffee_grammar.generate("chapelStory"))
        told_chapel = True


    elif not told_chapel and previous_lower == "weitz":

        koffee_print(koffee_grammar.generate("careerCenterStory"))
        told_careerCenter = True

    time.sleep(0.5)
    print("...Arrived at {}...".format(cap_current))
    time.sleep(0.5)


def feedback():
    """
    Generates a question to ask for user's feedback on the tour
    """
    global told_funfact

    koffee_print("Now we've reached the end of our tour. I'm very happy to have been your tour guide {}. How do you like the tour?".format(name))
    response = user_print()
    generate_sentiment(response)

    # check if at least a funFact is given
    if not told_funfact:
        koffee_print("Before you go, let me tell you one more thing about Carleton! " + koffee_grammar.generate("otherFunfacts"))


def farewell():
    """
    Generates farewell context-free-grammar 
    """
    koffee_print(koffee_grammar.generate("farewell"))


def cold_start_proof():
    """Calling Dialouge tag the first time may be a bit slow, so we do that here to get over with the cold start."""
    Response("This is ran so that all the libraries can be probably loaded before the user uses.")


def main():
    """
    Main function for the conversation
    """
    global name
    global major
    global start_building
    global previous_building
    global current_building
    global building_names

    cold_start_proof()
    building_dict = initialize_buiildings()
    print_text_art()
    introduction_conversation()

    # put start_building object in the list and random 2 more into the list
    building_names.remove(start_building.lower())
    picked_buildings = [building_dict[start_building.lower()]]
    for i in range(2): # random 2 more
        tmp_name = random.choice(building_names)
        building_names.remove(tmp_name)
        picked_buildings.append(building_dict[tmp_name])
    
    # go to each building
    for i in range(len(picked_buildings)):
        building = picked_buildings[i]
        current_building = building.name
        
        transition()
        visit_building(building)
        previous_building = current_building
        
        # don't print for the last destination
        if i < len(picked_buildings) - 1:
            koffee_print(koffee_grammar.generate("nextDestination") + " {}.".format(cap_first_character(picked_buildings[i+1].name)))
        

    feedback()
    farewell()

if __name__ == "__main__":
	main()
