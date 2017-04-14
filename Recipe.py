import json
import random

recipes = json.load(open("recipes.json"))

# returns the one specific matching recipe (if available)
def getRecipeByName(name):
    name = name.upper()
    for recipe in recipes:
        if recipe["name"].upper() == name:
            return recipe
    return None

# returns all the recipes that belong to that category (if available)
def getRecipeByCategory(category):
    category = category.upper()
    matches = []
    for recipe in recipes:
        if recipe["category"].upper() == category:
            matches.append(recipe)
    if len(matches) != 0:
        return matches
    return None

# returns a list of recipes that include that ingredient (if available)
# parameter listOfRecipes: for follow-up questions like the second ingredient that should be included
def getRecipeByIngredient(ingredient, listOfRecipes):
    matches = []
    ingredient = ingredient.upper()
    for recipe in listOfRecipes:
        ingredients = recipe["ingredients"]
        for ingr in ingredients:
            if ingredient in ingr.upper():
                matches.append(recipe)
    if len(matches) != 0:
        return matches
    return None


# Test getRecipeByName
#print(getRecipeByName("banana bread"))

# Test getRecipeByCategory
# list_recipes = getRecipeByCategory("main")
# recipe = list_recipes[0]
# x = recipe["name"]
# ingr = ''
# for ingredient in x:
#     ingr = ingr + ingredient + " "
# print(str(x))

# Test getRecipeByIngredient
matches = getRecipeByIngredient("pasta", recipes)
# matches = getRecipeByIngredient("salt", matches)       # in main - if it's the last ingredient from the user
                                                        # chose a random out of the matches-list with
                                                        # random.choice(matches) -> matches is the matches-list
# ingr = ''
# for ingredient in matches:
#     ingr = ingr + ingredient + ' '
# print(ingr)