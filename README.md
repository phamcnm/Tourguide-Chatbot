# Koffee the Tour Guide

## Goals

1. Koffee will bring the user to 3 buildings.
2. Koffee will give at least one funfact. If no funfact is said during the tour, Koffee will give a funfact before it says goodbye.

## Storyline (in order)

    Note: Most of the responses that Koffee make are generated with context-free-grammar

#### Introduction

Koffee will ask for a name and a prospective major. If a valid prospective major is given, it will bring the user to the building that has that major first.

### Transition

In between all the buildings is the transition phrase: a phrase while Koffee and the user are walking towards their destination. During the walk, Koffee will try to engage with the user by making some small talks with the user. After that, for some destinations, Koffee will also point up some important spots that they are walking by: bald spot, career center, and the chapel.

### Small Talk

In a small talk, Koffee will ask one of the three types of question. The question will either be an eliza question, a sentiment question, or a yes-no question. For the eliza question, Koffee will expect to response with eliza transformation. If it is not possible, it will response based on the sentiment of the string instead. For the sentiment question, Koffee will response based on the sentiment of the string. For the yes-no question, Koffee will look at the dialouge tag of the string. If the tag is a yes tag, Koffee will happily response back with context-free grammar. If the tag is something else, it will response based on sentiment.

For eliza question, if Koffee is able to response with eliza transformed text, it will wait for the user to type up another response (since our eliza transformations are mostly just asking the question back). If the new response is eliza transformable, it will transform and wait for response again. This will repeat for at most 3 times.

Before Koffee asks a question here, there is also a 33% chance that Koffee will bring up a quote that is generated from markov_model.

### Building (repeat 3 times)

When Koffee reaches the building, it will first check if this building has a major that the user is interesed in. If it does, it will mention that this building might be interesting for the user. After that, Koffee will use context-free-grammar to give a tour to the building. It will call generate on introduction nonterminal and features nonterminal first. Then, it will randomly called another nonterminal based on what nonterminals are left.

After the tour, Koffee will ask the user if the user has any question. If the reply contains a "no" tag, it will keep going, else it will try to look for keywords inside the reply. The keywords are the expected topics of questions that Koffee already has the answer in its grammar. If no keyword is found in the reply, it will tell the user to bring that question to the admission office.

### Feedback

Koffee will ask for the feedback of the tour and will response based on the sentiment of the response. If no funfact is given yet, it will be given here.

### Farewell

Koffee says goodbye.

## Global Features

### Keyphrase

When each response is being intitailzed, it will check if there is any keyphrase in the response or not. If there is any, Koffee will add in funfact based on the topic. Each topic will only be triggered once for the entire tour.

### Pickup Major

If the user doesn't give a valid major when Koffee asks the user in the introduction, the global variable major of the user will be set to "other". When that is the case, everytime the user types something in, Koffee will check if there is any keyword that might hint the major that the user might be interested in or not. If a major is picked up, Koffee will stop checking the responses after that for an interest in major.

Ex. if the user talks about watching movies, Koffee will think that the user as might be interesed in CAMS major. Thus, if Koffee gets to Weitz, it will mention to the user that this building might be interesting to the user because CAMS major is here.

### Profanity

Koffee will warn the user if any profanity is dectected in the response.

## Credits

Special Thanks to Carleton’s tour guiding program. We used a lot of facts from Carleton’s tour guide's booklet
