from mycroft import MycroftSkill, intent_file_handler
from mycroft.util.log import LOG
import requests
import time


API_KEY = '2432'
API_URL = 'https://www.thecocktaildb.com/api/json/v1/{}/'.format(API_KEY)
SEARCH = API_URL + 'search.php'


def search_cocktail(name):
    r = requests.get(SEARCH, params={'s': name})
    if 200 <= r.status_code < 300:
        return r.json()['drinks'][0]
    else:
        return None


def ingredients(drink):
    ingredients = []
    for i in range(1, 15):
        if not drink['strIngredient' + str(i)]:
            break
        ingredients.append(' '.join((drink['strMeasure' + str(i)],
                                    drink['strIngredient' + str(i)])))
    return ingredients


class CocktailSkill(MycroftSkill):
    @intent_file_handler('Recipie.intent')
    def get_recipie(self, message):
        cocktail = search_cocktail(message.data['drink'])
        if cocktail:
            self.speak_dialog('YouWillNeed', {
                'ingredients': ', '.join(ingredients(cocktail)[:-1]),
                'final_ingredient': ingredients(cocktail)[-1]})
            time.sleep(1)
            self.speak(cocktail['strInstructions'])


def create_skill():
    return CocktailSkill()
