import logging
from random import randint
import requests
from Recipe import *

from flask import Flask, render_template
from flask_ask import Ask, request, session, question, statement

from collections import deque

app = Flask(__name__)
ask = Ask(app, "/")
logging.getLogger('flask_ask').setLevel(logging.DEBUG)


def getIngredientsByRecipe(recipe):
    recipeDescription = getRecipeByName(recipe)
    recipe_ingr = recipeDescription["ingredients"]
    ingr = ''
    for ingredient in recipe_ingr:
        ingr = ingr + ingredient + " "
    return ingr

def getStepsOfRecipe(recipe):
    recipe_description = getRecipeByName(recipe)
    recipe_steps = recipe_description["method"]
    # Get the string with the method
    recipe_steps_str = recipe_steps[0]
    # Split
    steps = recipe_steps_str.split(". ")
    # steps = deque(steps)
    return steps

@ask.launch
def launch():
    return question("Hello, are you looking for a specific recipe or do you want me to suggest you something?").\
        reprompt("Can I suggest you any recipe?")


@ask.intent('RecommendationIntent')
def recommendation():
    session.attributes['state'] = 'recommendation'
    return question("What kind of dish do you want to make?").\
        reprompt("Sorry, I didn't get what kind of dish you want to make, could you repeat?")


@ask.intent('CategoryIntent', mapping={'category': 'Category'})
def get_category(category):
    session.attributes['category'] = category
    session.attributes['state'] = 'category'
    cat = "Do you have an ingredient you want to use or should I suggest a random one recipe?"
    return question(cat).\
        reprompt(cat)

"""
    list = getRecipeByCategory(category)
    random_id = randint(0, len(list)-1)
    question("The name of the selected recipe is " + recipe_name + " and its ingredients are " + ingr + ". Do you want to continu")."""

# We want Alexa to ask to the user to state at most 3 ingredients that he wants to use.
@ask.intent('StateIngrIntent', mapping={'ingredient': 'food'})
def get_ingr(ingredient):
    session.attributes['ingrs'].append({ingredient})
    if len(session.attributes['ingrs']) == 3:
        return statement("")recipe_intro()
    return question("Do you have another ingredient you want to use?"). \
        reprompt("Do you have another ingredient you want to use?")


"""
    recipe = list[random_id]
    recipe_name = recipe["name"]
    recipe_ingr = recipe["ingredients"]
    ingr = ''
    for ingredient in recipe_ingr:
        ingr = ingr + ingredient + " "
    question("The name of the selected recipe is " + recipe_name + " and its ingredients are " + ingr + ". Do you want to continu")."""



@ask.intent('SpecificIntent')
def specific():
    specQ = "Can you tell me the name of the recipe?"
    session.attributes['state'] = 'specificRecipe'
    return question(specQ).reprompt(specQ)


@ask.intent('SpecificNameIntent', mapping={'recipe': 'recipe'})
def specificRecipe(recipe):
    session.attributes['state'] = 'recipeIngredients'
    # Handling the case where the name of the recipe being said by the user is not stored in the file used by the app.
    if (getRecipeByName(recipe) == None):
        return statement("Sorry, the recipe " + recipe + " is not one of those available")
    else:
        ingr = getIngredientsByRecipe(recipe)
        recipeIntro = "The ingredients for " + recipe + " are: " + ingr + ". Do you want to continue or look for another recipe?"
        return question(recipeIntro).reprompt("Do you want to hear the ingredients again?")


@ask.intent('CheckIntent')
def check():
    session.attributes['state'] = 'checkIngredients'
    checkIngredients = "Do you have all the ingredients that you need for this recipe?"
    return question(checkIngredients).reprompt(checkIngredients)


@ask.intent('StepsIntent', mapping={'recipe': 'recipe'})
def nextStep(recipe):
    if (session.attributes['state'] == 'checkIngredients'):
        steps = getStepsOfRecipe(recipe)
        count = 0
        step = steps[count]
        session.attributes['recipeSteps'] = steps
        session.attributes['state'] = 'steps'
        count = count+1
        session.attributes['stepNum'] = count
        return question("Do this: " + step + ". Are you ready for the next step?").reprompt("Are you ready for the next step?")

    elif (session.attributes['state'] == 'steps' and len(session.attributes['recipeSteps']) != 0):
        steps = session.attributes['recipeSteps']
        count = session.attributes['stepNum']
        step = steps[count]
        session.attributes['recipeSteps'] = steps
        session.attributes['state'] = 'steps'
        return question("Now do this: " + step + ". Are you ready for the next step?").reprompt("Are you ready for the next step?")

    elif (session.attributes['state'] == 'steps' and len(session.attributes['recipeSteps']) == 0):
        return statement("You are done! Your food look delicious") # or should we return stop() ????

    else:
        # Handle the case in which the Steps intent is not activated in the possible correct states
        not_steps = "I think this is not the right moment to tell you the steps of the recipe, can I help in another way?"
        return question(not_steps).reprompt(not_steps)




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