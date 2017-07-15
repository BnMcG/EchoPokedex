import logging
import requests

from flask import Flask, render_template
from flask_ask import Ask, statement, question

app = Flask(__name__)
ask = Ask(app, "/")

logging.getLogger("flask_ask").setLevel(logging.DEBUG)


def do_lookup(id):
    try:
        r = requests.get('http://pokeapi.co/api/v2/pokemon/' + id)
        data = r.json()

        if data['species'] is not None and len(data['species']) > 0:
            species_request = requests.get(data['species']['url'])
            species = species_request.json()
        else:
            pass

        types = []
        for entry in data['types']:
            types.append(entry['type']['name'])

        types = '/'.join(types)

        evolution, evolution_text = None, None

        try:
            evolution_request = requests.get(species['evolution_chain']['url'])
            evolution = evolution_request.json()
        except Exception:
            pass

        if len(evolution['chain']['evolves_to']) > 0:
            evolution_text = 'At level ' + str(evolution['chain']['evolves_to'][0]['evolution_details'][0]['min_level']) + ', ' + data['name'] + ' evolves into ' + evolution['chain']['evolves_to'][0]['species']['name']

        if evolution_text is not None:
            response = data['name'] + '. A ' + types + ' Pokemon. ' + species['flavor_text_entries'][1]['flavor_text'] + '. ' + evolution_text
        else:
            response = data['name'] + '. A ' + types + ' Pokemon. ' + species['flavor_text_entries'][1]['flavor_text']

        return response
    except Exception as e:
        return str('Sorry. I could not find that Pokemon. Try specifying the Pokemon\'s number as a word. For example: two hundred and fourty one.')

@ask.launch
def launch():
    return question('Pokedex online! What do you want to lookup?')

@ask.intent('LookupIdIntent')
def lookup_id(id):
    return statement(do_lookup(id))

@ask.intent('LookupIntent')
def lookup(name):
    return statement(do_lookup(name))

if __name__ == '__main__':
    app.run(debug=True)
