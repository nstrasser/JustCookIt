import logging
from random import randint
from Recipe import *

from flask import Flask, render_template
from flask_ask import Ask, request, session, question, statement

app = Flask(__name__)
ask = Ask(app, "/")
logging.getLogger('flask_ask').setLevel(logging.DEBUG)


# function to get the ingredients you need for the recipe. The list is converted into a string "ingr".
def getIngredientsByRecipe(recipe):
    recipeDescription = getRecipeByName(recipe)
    recipe_ingr = recipeDescription["ingredients"]
    ingr = ''
    for ingredient in recipe_ingr:
        ingr = ingr + ingredient + " "
    return ingr

# function to retrieve the method to cook the recipe. The string is converted in a list of strings, each element of the
# list is a step of the recipe
def getStepsOfRecipe(recipe):
    recipe_description = getRecipeByName(recipe)
    recipe_steps = recipe_description["method"]
    # Get the string with the method
    recipe_steps_str = recipe_steps[0]
    # Split
    steps = recipe_steps_str.split(". ")
    # steps = deque(steps)
    return steps

# function to get the title and the ingredients of the recipe.
# Used in RandomIntent and StateIngrIntent
def get_intro(recipe):
    recipe_ingr = recipe["ingredients"]
    recipe_name = recipe['name']
    ingr = ''
    for ingredient in recipe_ingr:
        ingr = ingr + ingredient + " "
    return "The name of this recipe is " + str(recipe_name) + " . Its ingredients are " + ingr


@ask.launch
def launch():
    return question("Hello, are you looking for a specific recipe or do you want me to suggest you something?"). \
        reprompt("Can I suggest you any recipe?")


# If the user asked for a recommendation when the skill was launched, Alexa will ask the category of the dish that the user wants to make
@ask.intent('RecommendationIntent')
def recommendation():
    session.attributes['state'] = 'recommendation'
    return question("What kind of dish do you want to make?"). \
        reprompt("Sorry, I didn't get what kind of dish you want to make, could you repeat?")


# Alexa understand the category. The user now has to state 3 ingredients or ask for a suggested recipe by Alexa
@ask.intent('CategoryIntent', mapping={'category': 'Category'})
def get_category(category):
    session.attributes['category'] = category
    session.attributes['state'] = 'category'
    cat = "What ingredient do you want to use or should I suggest a random recipe?"
    return question(cat). \
        reprompt(cat)

# Alexa selects a random recipe, tells the name and the ingredients and then ask the user if he wants to continue
# with that one or hear another one.
@ask.intent('RandomIntent')
def get_random():
    list_recipes = getRecipeByCategory(session.attributes['category'])
    random_id = randint(0, len(list_recipes) - 1)
    recipe = list_recipes[random_id]
    session.attributes['recipe'] = recipe
    print(get_intro(recipe))
    question(get_intro(recipe) + "Do you want to continue with this recipe or hear another one?"). \
        reprompt("Do you want to continue with the recipe for " + recipe['name'] + " or do you want to hear another one?")


# We want Alexa to ask to the user to state at most 3 ingredients that he wants to use.
@ask.intent('StateIngrIntent', mapping={'ingredient': 'food'})
def get_ingr(ingredient):
    session.attributes['state'] = 'ingredient'
    #if session.attributes['ingrs'] == None:
    ingred = []
    session.attributes['ingrs'] = ingred

    session.attributes['ingrs'].append(ingredient)
    if len(session.attributes['ingrs']) == 3:
        filteredList = get_recipes_by_ingrs()
        randomId = randint(0, len(filteredList) - 1)
        random_recipe = filteredList[randomId]
        session.attributes['recipe'] = random_recipe
        return question(get_intro(random_recipe) + "Do you want to continue with this recipe?"). \
            reprompt("Do you want to continue with " + str(random_recipe['name']))
    return question("What else?"). \
        reprompt("Please tell me an ingredient?")


# function to retrieve recipes with the ingredients listed by the user
def get_recipes_by_ingrs():
    list_ingrs = session.attributes["ingrs"]
    filteredlist = None
    for ingr in list_ingrs:
        filteredlist = getRecipeByIngredient(ingr, filteredlist)
    return filteredlist

# Alexa prompt the user to tell her the name of a specific recipe he wants to cook
@ask.intent('SpecificIntent')
def specific():
    specQ = "Can you tell me the name of the recipe?"
    session.attributes['state'] = 'specificRecipe'
    return question(specQ).reprompt(specQ)

# Alexa tells the ingredient needed for the recipe and ask if the user wants to continue with it or choose another one
@ask.intent('SpecificNameIntent', mapping={'recipe': 'Name'})
def specificRecipe(recipe):
    session.attributes['state'] = 'recipeIngredients'
    # Handling the case where the name of the recipe being said by the user is not stored in the file used by the app.
    if (getRecipeByName(recipe) == None):
        return statement("Sorry, the recipe " + recipe + " is not one of those available")
    else:
        session.attributes['recipe'] = recipe
        ingr = getIngredientsByRecipe(recipe)
        recipeIntro = "The ingredients for " + recipe + " are: " + ingr + ". Do you want to continue or look for another recipe?"
        return question(recipeIntro).reprompt("Do you want to hear the ingredients again?")


# Ask the user if he has all the ingredients for the recipe before starting guiding him through the steps
@ask.intent('CheckIntent')
def check():
    session.attributes['state'] = 'checkIngredients'
    check_ingredients = "Do you have all the ingredients that you need for this recipe?"
    return question(check_ingredients).reprompt(check_ingredients)

# Give the recipe step by step
@ask.intent('StepsIntent')
def nextStep():
    # Case 1: the user just said that he has all the ingredients, thus Alexa has to say the first step of the recipe
    if (session.attributes['state'] == 'checkIngredients'):
        recipe = session.attributes['recipe']
        steps = getStepsOfRecipe(recipe)
        count = 0
        step = steps[count]
        session.attributes['recipeSteps'] = steps
        session.attributes['state'] = 'steps'
        session.attributes['stepNum'] = count
        return question("Do this: " + step + ". Are you ready for the next step?").reprompt(
            "Are you ready for the next step?")

    # Case 2: Alexa has already said one or more steps but the recipe is not over yet
    elif (session.attributes['state'] == 'steps' and len(session.attributes['recipeSteps']) != 0):
        steps = session.attributes['recipeSteps']
        count = session.attributes['stepNum']
        step = steps[count]
        session.attributes['recipeSteps'] = steps
        session.attributes['state'] = 'steps'
        return question("Now do this: " + step + ". Are you ready for the next step?").reprompt(
            "Are you ready for the next step?")

    # Case 3: The recipe has been completed and the app can be closed
    elif (session.attributes['state'] == 'steps' and len(session.attributes['recipeSteps']) == 0):
        return statement("You are done! Your food look delicious")  # or should we return stop() ????

    # Handle the case in which the Steps intent is not activated in the possible correct states
    else:
        not_steps = "I think this is not the right moment to tell you the steps of the recipe, can I help in another way?"
        return question(not_steps).reprompt(not_steps)


@ask.intent('AMAZON.NoIntent')
def no():
    state = session.attributes['state']
    # The user does not want to give any more ingredients in StateIngrIntent
    if state == 'ingredient':
        recipeList = get_recipes_by_ingrs()
        randomId = randint(0, len(recipeList) - 1)
        recipe = recipeList[randomId]
        return question(get_intro(recipe) + "Do you want to continue with this recipe?"). \
            reprompt("Do you want to continue with " + str(recipe['name']))

    # The user does not have all the ingredients for the recipe when asked at "CheckIntent". Alexa search for another random recipe
    elif state == 'checkIngredients':
        if session.attributes['ingrs'] != None:
            return get_random()
        else:
            recipeList = get_recipes_by_ingrs()
            randomId = randint(0, len(recipeList) - 1)
            recipe = recipeList[randomId]
            return question(get_intro(recipe) + "Do you want to continue with this recipe?"). \
                reprompt("Do you want to continue with " + str(recipe['name']))

    # The user is not ready to go to the next step, so Alexa tells him the last step
    elif state == 'steps':
        return nextStep()

    # Handle the case that no is not being said in one of the states above
    else:
        return question("I can't help you. Try again!")


@ask.intent('AMAZON.YesIntent')
def yes():
    # The user has all the ingredients and he is ready to start cooking
    if (session.attributes['state'] == 'checkIngredients'):
        return nextStep()

    # The user is ready to move to the next step of the recipe
    elif (session.attributes['state'] == 'steps'):
        count = session.attributes['stepNum']
        count = count + 1
        session.attributes['stepNum'] = count
        return nextStep()

    # Handle the case that yes is not being said in one of the states above
    else:
        yes_wrong = "Sorry, I am not sure what are you saying yes for. Can I help you with anything?"
        return question(yes_wrong).reprompt(yes_wrong)


@ask.intent('AMAZON.NextIntent')
def next_recipe():
    # Ask Alexa to suggest another recipe
    return get_random()


@ask.intent('AMAZON.HelpIntent')
def help_recipe():
    # Ask for help
    help_text = "How can I help you with this recipe?"
    return question(help_text).reprompt(help_text)


@ask.intent('AMAZON.StopIntent')
def stop():
    # Close the app. Alexa will greet you.
    bye_text = "This seemed a delicious recipe."
    return statement(bye_text)


@ask.intent('AMAZON.CancelIntent')
def cancel():
    # Close the app.
    return stop()


@ask.session_ended
def session_ended():
    return "", 200


# this final statement is required to run the app defined above
if __name__ == '__main__':
    app.run(debug=True)
