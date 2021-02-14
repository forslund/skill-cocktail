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
from mycroft import MycroftSkill, intent_handler, AdaptIntent
import requests
import time
from google_trans_new import google_translator 

API_KEY = '2432'
API_URL = 'https://www.thecocktaildb.com/api/json/v1/{}/'.format(API_KEY)
SEARCH = API_URL + 'search.php'
RANDOM = API_URL + 'random.php'

def search_cocktail(name):
    """Search the Cocktails DB for a drink."""
    r = requests.get(SEARCH, params={'s': name})
    if (200 <= r.status_code < 300 and 'drinks' in r.json() and
            r.json()['drinks']):
        return r.json()['drinks'][0]
    else:
        return None


def search_ingredient(ingedient):
    """Search the Cocktails DB for a drink."""
    r = requests.get(SEARCH, params={'s': name})
    if (200 <= r.status_code < 300 and 'drinks' in r.json() and
            r.json()['drinks']):
        return r.json()['drinks'][0]
    else:
        return None


def random_cocktail():
    """Get a random drink."""
    r = requests.get(RANDOM)
    if (200 <= r.status_code < 300 and 'drinks' in r.json() and
            r.json()['drinks']):
        return r.json()['drinks'][0]
    else:
        return None


def ingredients(drink, lang):
    """Get ingredients from drink data from the cocktails DB."""
    ingredients = []
    for i in range(1, 15):
        ingredient_key = 'strIngredient' + str(i)
        measure_key = 'strMeasure' + str(i)
        if not drink[ingredient_key]:
            break
        if drink[measure_key] is not None:
            ingredients.append(' '.join((drink[measure_key],
                                         drink[ingredient_key])))
        else:  # If there is no measurement for the ingredient ignore it
            ingredients.append(drink[ingredient_key])

    return nice_ingredients(ingredients, lang)


def nice_ingredients(ingredients, lang):
    """Make ingredient list easier to pronounce."""
    translator = google_translator()
    units = {
            'oz': 'ounce',
            '1 tbl': '1 table spoon',
            'tbl': 'table spoons',
            '1 tsp': '1 tea spoon',
            'tsp': 'tea spoons',
            'ml ': 'milliliter ',
            'cl ': 'centiliter '
    }
    ret = []
    for i in ingredients:
        for word, replacement in units.items():
            i = i.lower().replace(word, replacement)
        if i is not None:
            if lang != 'en':
                i = translator.translate(i, lang_src='en', lang_tgt=lang)
            ret.append(i)
    return ret


class CocktailSkill(MycroftSkill):

    instructionMapper = {
        "de": "strInstructionsDE",
        "en": "strInstructions",
        "fr": "strInstructionsFR",
        "es": "strInstructionsES"
        }

    def initialize(self):
        self.language = self.config_core.get('lang').split('-')[0]
        self.instructionKey = self.instructionMapper.get(self.language, "strInstructions")

    @intent_handler('Random.intent')
    def get_random(self, message):
        cocktail = random_cocktail()
        self.speak_dialog("RandomDrink", {"drink": cocktail['strDrink']})
        time.sleep(1)
        self.handle_cocktail(cocktail)

    @intent_handler('Recipe.intent')
    def get_recipe(self, message):
        cocktail = search_cocktail(message.data['drink'])
        self.handle_cocktail(cocktail)

    def handle_cocktail(self, cocktail):
        if cocktail:
            ingreds = ingredients(cocktail, self.language)
            self.speak_dialog('YouWillNeed', {
                'ingredients': ', '.join(ingreds[:-1]),
                'final_ingredient': ingreds[-1]})
            time.sleep(1)
            instructions = cocktail.get(self.instructionKey, None)
            if instructions is None:
                instructions = cocktail["strInstructions"]
            self.speak(instructions)
            self.set_context('IngredientContext', str(', '.join(ingreds)))
        else:
            self.speak_dialog('NotFound')

    def repeat_ingredients(self, ingredients):
        self.speak(ingredients)

    @intent_handler('Needed.intent')
    def get_ingredients(self, message):
        cocktail = search_cocktail(message.data['drink'])
        if cocktail:
            self.speak_dialog('YouWillNeed', {
                'ingredients': ', '.join(ingredients(cocktail)[:-1]),
                'final_ingredient': ingredients(cocktail)[-1]})
            self.set_context('IngredientContext', str(ingredients(cocktail)))
        else:
            self.speak_dialog('NotFound')

    @intent_handler(AdaptIntent("").require('Ingredients').require('What')
                                   .require('IngredientContext'))
    def what_were_ingredients(self, message):
        """Context aware handler if the user asks for a repeat."""
        return self.repeat_ingredients(message.data['IngredientContext'])

    @intent_handler(AdaptIntent("").require('Ingredients').require('TellMe')
                                   .require('Again')
                                   .require('IngredientContext'))
    def tell_ingredients_again(self, message):
        return self.repeat_ingredients(message.data['IngredientContext'])


def create_skill():
    return CocktailSkill()
