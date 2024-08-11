# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
#
import time

import requests
from ovos_bus_client.message import Message
from ovos_workshop.decorators import intent_handler
from ovos_workshop.intents import IntentBuilder
from ovos_workshop.skills import OVOSSkill

API_KEY = "2432"
API_URL = f"https://www.thecocktaildb.com/api/json/v1/{API_KEY}/"
SEARCH = API_URL + "search.php"
RANDOM = API_URL + "random.php"


def search_cocktail(name):
    """Search the Cocktails DB for a drink."""
    r = requests.get(SEARCH, params={"s": name}, timeout=3)
    if (200 <= r.status_code < 300 and "drinks" in r.json() and
            r.json().get("drinks")):
        return r.json()["drinks"][0]
    return None


def search_ingredient(ingredient):
    """Search the Cocktails DB for a drink."""
    r = requests.get(SEARCH, params={"s": ingredient}, timeout=3)
    if (200 <= r.status_code < 300 and "drinks" in r.json() and
            r.json()["drinks"]):
        return r.json()["drinks"][0]
    return None


def random_cocktail():
    """Get a random drink."""
    r = requests.get(RANDOM, timeout=3)
    if (200 <= r.status_code < 300 and "drinks" in r.json() and
            r.json()["drinks"]):
        return r.json()["drinks"][0]
    return None


def ingredients(drink):
    """Get ingredients from drink data from the cocktails DB."""
    ingredients = []
    for i in range(1, 15):
        ingredient_key = "strIngredient" + str(i)
        measure_key = "strMeasure" + str(i)
        if not drink[ingredient_key]:
            break
        if drink[measure_key] is not None:
            ingredients.append(" ".join((drink[measure_key],
                                         drink[ingredient_key])))
        else:  # If there is no measurement for the ingredient ignore it
            ingredients.append(drink[ingredient_key])

    return nice_ingredients(ingredients)


def nice_ingredients(ingredients):
    """Make ingredient list easier to pronounce."""
    units = {
        "oz": "ounce",
        "1 tbl": "1 table spoon",
        "tbl": "table spoons",
        "1 tsp": "tea spoon",
        "tsp": "tea spoons",
        "ml ": "milliliter ",
        "cl ": "centiliter ",
    }
    ret = []
    for i in ingredients:
        for word, replacement in units.items():
            i = i.lower().replace(word, replacement)
        ret.append(i)
    return ret


class CocktailSkill(OVOSSkill):
    @intent_handler("Random.intent")
    def get_random(self, message: Message):
        cocktail = random_cocktail()

        self.speak_dialog("RandomDrink", {"drink": cocktail["strDrink"]})
        time.sleep(1)
        self.speak_dialog(
            "YouWillNeed",
            {
                "ingredients": ", ".join(ingredients(cocktail)[:-1]),
                "final_ingredient": ingredients(cocktail)[-1]
            },
        )
        time.sleep(1)
        self.speak(cocktail["strInstructions"])
        self.set_context("IngredientContext", str(ingredients(cocktail)))

    @intent_handler("Recipe.intent")
    def get_recipe(self, message: Message):
        cocktail = search_cocktail(message.data["drink"])
        if cocktail:
            self.speak_dialog(
                "YouWillNeed",
                {
                    "ingredients": ", ".join(ingredients(cocktail)[:-1]),
                    "final_ingredient": ingredients(cocktail)[-1]},
            )
            time.sleep(1)
            self.speak(cocktail["strInstructions"])
            self.set_context("IngredientContext", str(ingredients(cocktail)))
        else:
            self.speak_dialog("NotFound")

    def repeat_ingredients(self, ingredients):
        self.speak(ingredients)

    @intent_handler("Needed.intent")
    def get_ingredients(self, message: Message):
        cocktail = search_cocktail(message.data["drink"])
        if cocktail:
            self.speak_dialog(
                "YouWillNeed",
                {"ingredients": ", ".join(ingredients(cocktail)[:-1]),
                 "final_ingredient": ingredients(cocktail)[-1]},
            )
            self.set_context("IngredientContext", str(ingredients(cocktail)))
        else:
            self.speak_dialog("NotFound")

    @intent_handler(
            IntentBuilder("").require("Ingredients")
                             .require("What")
                             .require("IngredientContext"))
    def what_were_ingredients(self, message: Message):
        """Context aware handler if the user asks for a repeat."""
        return self.repeat_ingredients(message.data["IngredientContext"])

    @intent_handler(
        IntentBuilder("").require("Ingredients")
                         .require("TellMe")
                         .require("Again")
                         .require("IngredientContext")
    )
    def tell_ingredients_again(self, message: Message):
        return self.repeat_ingredients(message.data["IngredientContext"])
