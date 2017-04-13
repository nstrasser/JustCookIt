import logging
from random import randint
from Recipe import *

from flask import Flask, render_template
from flask_ask import Ask, request, session, question, statement

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


def get_intro(recipe):
    recipe_ingr = recipe["ingredients"]
    recipe_name = recipe['name']
    ingr = ''
    for ingredient in recipe_ingr:
        ingr = ingr + ingredient + " "
    return "The name of this recipe is " + str(recipe_name) + " . Its ingredients are " + ingr;


@ask.launch
def launch():
    return question("Hello, are you looking for a specific recipe or do you want me to suggest you something?"). \
        reprompt("Can I suggest you any recipe?")


@ask.intent('RecommendationIntent')
def recommendation():
    session.attributes['state'] = 'recommendation'
    return question("What kind of dish do you want to make?"). \
        reprompt("Sorry, I didn't get what kind of dish you want to make, could you repeat?")


@ask.intent('CategoryIntent', mapping={'category': 'Category'})
def get_category(category):
    session.attributes['category'] = category
    session.attributes['state'] = 'category'
    cat = "What ingredient do you want to use or should I suggest a random recipe?"
    return question(cat). \
        reprompt(cat)


@ask.intent('RandomIntent')
def get_random():
    list = getRecipeByCategory(session.attributes['category'])
    random_id = randint(0, len(list) - 1)
    question(get_intro(list[random_id]) + "Do you want to continue with this recipe or hear another one?"). \
        reprompt("Do you want to continue with this" + list[random_id]['name'] + " recipe or hear another one?")


@ask.intent('StateIngrIntent', mapping={'ingredient': 'food'})
def get_ingr(ingredient):
    session.attributes['ingrs'].append({ingredient})
    if len(session.attributes['ingrs']) == 3:
        filteredList = get_recipe_by_ingrs()
        randomId = randint(0, len(filteredList) - 1)
        random_recipe = filteredList[randomId]
        return question(get_intro(random_recipe) + "Do you want to continue with this recipe?"). \
            reprompt("Do you want to continue with " + str(random_recipe['name']))
    return question("What else?"). \
        reprompt("Please tell me an ingredient?")


def get_recipe_by_ingrs():
    list_ingrs = session.attributes["ingrs"]
    filteredlist = None
    for ingr in list_ingrs:
        filteredlist = getRecipeByIngredient(ingr, filteredlist)
    return filteredlist


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


@ask.session_ended
def session_ended():
    return "", 200


# this final statement is required to run the app defined above
if __name__ == '__main__':
    app.run(debug=True)
