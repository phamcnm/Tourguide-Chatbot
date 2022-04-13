# Koffee the Tour Guide

### Authors
 Yuting Su, Minh Pham, PJ Sangvong

## Samples
    (NAMED ENTITTY RECOGNITION)
    Koffee: Hi I'm Koffee, your tour guide for today. Welcome to Carleton! What's your name?  
    You:    I'm PJ.
    Koffee: So sorry, but I didn't catch your name. What is your name again? Perhaps give me your full      
            name? 
    You:    Sukrit Sangvong 
    Koffee: Nice to meet you Sukrit Sangvong! 
    Koffee: What's your prospective major? or what are the things you enjoy doing? 
    You:    Maybe CS. I like programming a lot.
    Koffee: Awesome! Computer Science sounds like a good fit for you. Let's start our tour at Olin, 
            follow me! 
            
    (ELIZA TRANSFORMATION)
    Koffee: Is hot dog a sandwich? 
    You:    I don't know. I don't eat hot dog.
    Koffee: Do you like to know? 
    You:    Yes. Is it a sandwich?
    Koffee: Do you like to be? 
    You:    I don't think so.
    Koffee: Do you like to think? 
    
    (SENTIMENTAL ANALYSIS)
    You:    Ahhhh. Yeaa
    Koffee: You are speaking facts.
    ...
    Koffee: How is the tour so far? 
    You:    I like it. It is awesome!    
    Koffee: I like what you are saying! 
    
    (KEYPHRASE TRIGGER)
    Koffee: Any Question? 
    You:    How's the workload at Carleton?
    Koffee: Hmmmm for workload, I think it depends. The workload for 6 credits classes are generally 
            big, and people usually take 18 credits per term. But if you think you are too busy or too 
            free during one of the terms, you can always choose to uderload or overload. 
    Koffee: We are heading towards Libe. 
    
    (CONTEXT FREE GRAMMAR)
    Koffee: This building may interest you! It is a building for Computer Science. 
    Koffee: Welcome to Olin Hall! This building just got renovated and just opened for students to 
            use in Fall 2020. The building is the third science building at Carleton and is fully connected 
            to Anderson on all three floors. 
    Koffee: There is a huge Student Lounge on the thrid floor that takes up almost the entire length 
            of the building. It is a space for computer science students to work on homework, but it 
            is also opened for any students to come and work as well. There are a lot of labs scatter 
            on all the floors, including the underground floor. The labs included Psychology labs, 
            GIS labs, and a lot of computer labs. 
    Koffee: There is not a particular office in this building. However, faculties for CS, Psychology, 
            and Physics and Astronomy all have their offices in this building, so if you need to come 
            to office hours or just say hi to your professors from any of these departments, this is 
            the building. 
    
## How To Run

 1. Run `./setup` to install all the dependencies
 2. Run `python3 koffee.py` and start chatting!
    
## Goals

1. Koffee will bring the user to 3 buildings.
2. Koffee will give at least one funfact. If no funfact is said during the tour, Koffee will give a fun fact before it says goodbye.

## Storyline (in order)

    Note: Most of the responses that Koffee make are generated with context-free-grammar

#### Introduction

Koffee will ask for a name and a prospective major. If a valid prospective major is given, it will bring the user to the building that has that major first.

### Transition

In between all the buildings is the transition phrase: a phrase while Koffee and the user are walking towards their destination. During the walk, Koffee will try to engage with the user by making small talks with the user. After that, depending on the destinations, Koffee will also point up some important places that they would actually be walking by in real life, such as the bald spot, the career center, and the chapel.

### Small Talk

In a small talk, Koffee will ask one of the three types of question. The question will either be an ELIZA question (https://web.njit.edu/~ronkowit/eliza.html), a sentiment question, or a yes-no question. For the eliza question, Koffee will expect to response with eliza transformation. If it is not possible, it will instead respond based on its sentiment analysis of the string. For the sentiment question, Koffee will always respond based on the sentiment of the string. For the yes-no question, Koffee will look at the dialouge tag of the string. If the tag is a yes tag, Koffee will use context-free grammar in its response. If the tag is something else, it will response based on sentiment.

For eliza question, if Koffee is able to respond with eliza transformed text, it will wait for the user to type up another response (since our eliza transformations are mostly just asking the question back). If the new response is eliza transformable, it will transform and wait for response again. This will repeat for at most 3 times.

Before Koffee asks a question here, there is also a 33% chance that Koffee will bring up a quote that is generated from markov_model.

### Building (repeat 3 times)

When Koffee reaches the building, it will first check if this building has the department that the user is interesed in. If it does, it will mention that this building might be interesting for the user. After that, Koffee will use context-free-grammar to give a tour to the building. It will call generate on introduction nonterminal and features nonterminal first. Then, it will randomly call another nonterminal based on what nonterminals are left.

After the tour, Koffee will ask the user if the user has any questions. If the reply contains a "no" tag, it will keep going, else it will try to look for keywords inside the reply. The keywords are the expected topics of questions that Koffee already has the answer in its grammar. If no keyword is found in the reply, it will refer users to the the admission office.

### Feedback

Koffee will ask for the feedback of the tour and will respond based on the sentiment of user's input. If no fun fact is given so far, it will be given here.

### Farewell

Koffee says goodbye.

## Global Features

### Keyphrase

When each response is being intitailzed, it will check if there is any keyphrase in the response or not. If there is any, Koffee will add in a fun fact based on the topic. Each topic will only be triggered once for the entire tour.

### Pickup Major

If the user doesn't give a valid major when Koffee asks the user in the introduction, the global variable major of the user will be set to "other". When that is the case, everytime the user types something in, Koffee will check if there is any keyword that might hint the major that the user might be interested in or not. If a major is picked up, Koffee will stop checking the responses after that for an interest in major.

Ex. if the user talks about watching movies, Koffee will think that the user as might be interesed in CAMS major. Thus, if Koffee gets to Weitz, it will mention to the user that this building might be interesting to the user because CAMS major is here.

### Profanity

Koffee will warn the user if any profanity is dectected in the response.

## Credits

Special Thanks to Carleton’s tour guiding program. We used a lot of facts from Carleton’s tour guide's booklet
