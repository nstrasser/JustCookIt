import logging
from random import randint
import requests
from Recipe import *

from flask import Flask, render_template
from flask_ask import Ask, request, session, question, statement


app = Flask(__name__)
ask = Ask(app, "/")
logging.getLogger('flask_ask').setLevel(logging.DEBUG)

@ask.launch
def launch():
    return question("Hello, are you looking for a specific recipe or do you want me to suggest you something?").\
        reprompt("Can I suggest you any recipe?")


@ask.intent('RecommendationIntent')
def recommendation():
    return question("What kind of dish do you want to make?").\
        reprompt("Sorry, I didn't get what kind of dish you want to make, could you repeat?")

@ask.intent('CategoryIntent', mapping={'category': 'Category'})
def getCategory(category):
    session.attributes['category'] = category
    return question("Do you have an ingredient you want to use or should I suggest a random one recipe?").\
        reprompt("Do you have an ingredient you want to use or should I suggest a random one recipe?")

"""
    list = getRecipeByCategory(category)
    random_id = randint(0, len(list)-1)
    recipe = list[random_id]
    recipe_name = recipe["name"]
    recipe_ingr = recipe["ingredients"]
    ingr = ''
    for ingredient in recipe_ingr:
        ingr = ingr + ingredient + " "
    question("The name of the selected recipe is " + recipe_name + " and its ingredients are " + ingr + ". Do you want to continu")."""


# We want Alexa to ask to the user to state at most 3 ingredients that he wants to use.
@ask.intent('StateIngrIntent')


@ask.intent('SpecificIntent')
def specific():
    specQ = "Can you tell me the name of the recipe?"
    return question(specQ).reprompt(specQ)
# We should have something to handle the case where the name of a recipe is said by the user but the recipe is not stored in Just Cook It

# For this intent we need the AMAZON.NUMBER in the intent list on amazon developer. Similar to what we did for hello python app
@ask.intent('SpecificNameIntent', mapping={'name': 'name'})
def specificRecipe(name):
    # session.attributes['name'] = name
    return statement("You asked me about " + name + "Here are the ingredients you need " + )
# how do we filter out of our json file just the recipe that the user said the name of and how we can get its ingredients?


@ask.intent('AMAZON.NoIntent')



@ask.intent('AMAZON.YesIntent')



@ask.intent('AMAZON.NextIntent')



@ask.intent('AMAZON.HelpIntent')
def help():
    help_text = "How can I help you with this recipe?"
    return question(help_text).reprompt(help_text)


@ask.intent('AMAZON.StopIntent')
def stop():
    bye_text = "This seemed a delicious recipe."
    return statement(bye_text)


@ask.intent('AMAZON.CancelIntent')
def cancel():
    return stop()



"""
@ask.intent('HelloWorldIntent')
def hello_world():
    return statement("Where is Ham Ham?")


@ask.intent('AMAZON.HelpIntent')
def help():
    help_text = "Ask me to say Hi, dude."
    return question(help_text).reprompt(help_text)
# If no response ask again, if second time there is yet no response, end session



@ask.intent('AMAZON.StopIntent')
def stop():
    bye_text = "Hasta la vista"
    return statement(bye_text)


@ask.intent('AMAZON.CancelIntent')
def cancel():
    return stop()


@ask.intent('NumIntent', mapping={'number': 'number'})
def number_intent(number):
    session.attributes['number'] = number
    link = 'http://numbersapi.com/' + number
    num_response = requests.get(link)
    return question("The fact is " + num_response.text).reprompt("Ask me more about numbers, dude.")


@ask.intent('WhatNumIntent')
def what_num():
    number = session.attributes['number']
    return statement("You asked me about " + str(number))


@ask.intent('ItalyIntent')
def italy():
    italy_text = "Why are you in Scotland when it is sunny in Italy?"
    return statement(italy_text)


@ask.intent('GetItalianFactIntent')
def get_it_fact():
    num_facts = 13  # increment this when adding a new fact template
    fact_index = randint(0, num_facts-1)
    fact_text = render_template('italy_fact_{}'.format(fact_index))
    card_title = render_template('card_title')
    return statement(fact_text).simple_card(card_title, fact_text)
"""

@ask.session_ended
def session_ended():
    return "", 200


# this final statement is required to run the app defined above
if __name__ == '__main__':
    app.run(debug=True)