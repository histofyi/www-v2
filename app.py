from typing import Dict, List
import json

import toml
import datetime

from flask import Flask, request, make_response, Response, redirect

from functions.forms import request_variables
from functions.sitespecific import lookup_pdb_code, get_random
from functions.files import load_json
from functions.sets import hydrate_set


def create_app():
    """
    Creates an instance of the Flask app, and associated configuration and blueprints registration for specific routes. 

    Configuration includes

    - Relevant secrets stored in the config.toml file
    - Storing in configuration a set of credentials for AWS (decided upon by the environment of the application e.g. development, live)
    
    Returns:
            A configured instance of the Flask app

    """
    app = Flask(__name__)

    app.config.from_file('config.toml', toml.load)
    app.secret_key = app.config['SECRET_KEY']

    # removing whitespace from templated returns    
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    return app


app = create_app()



@app.before_first_request
def load_data():
    """
    This is a function which loads the generated datasets which are used by the site.

    By loading them in here, we can reduce S3 calls and speed the app up significantly.
    """
    datasets = ['pdb_codes','collections','index','ordering','sets','core']
    app.data = {}
    for dataset in datasets:
        app.data[dataset] = load_json(dataset)



@app.route('/')
def home_handler():
    """
    This is a placeholder home action.

    The real one will show collections and latest structures
    """
    page_data = {
        'collections':app.data['collections']['homepage'],
        'latest':hydrate_set(app.data['sets']['latest'],app.data['core'])
    }
    return page_data


@app.route('/structures/lookup/')
@app.route('/structures/lookup')
def structure_lookup_handler():
    """
    This function is the structure lookup handler.

    It looks up pdb codes entered into the lookup form box, or in the query string

    If a single result is found, it redirects to the structure view page for that pdb code

    If there's no single match, some suggestions are given
    """
    data = request_variables(None, params=['pdb_code'])
    if data['pdb_code'] is not None:
        pdb_code = data['pdb_code'].lower()
        matches = lookup_pdb_code(pdb_code, app.data['pdb_codes'])
        if matches['match'] == 'exact' or len(matches['best_matches']) == 1:
            return {'redirect_to':f'/structures/view/{pdb_code}'}
    else:
        matches = lookup_pdb_code('', app.data['pdb_codes'])
    return matches


@app.route('/structures/view/<string:pdb_code>/')
@app.route('/structures/view/<string:pdb_code>')
def structure_view_handler(pdb_code):
    """
    This function is the structure view handler

    """
    if pdb_code is not None:
        pdb_code = pdb_code.lower()  
        if pdb_code in app.data['pdb_codes']:
            # fetch the data on the structure
            return {'pdb_code':pdb_code}
        else:
            matches = lookup_pdb_code(pdb_code, app.data['pdb_codes'])
            return {
                'error':'not_in_pdb_codes',
                'matches': matches
            }
    else:
        matches = get_random(app.data['pdb_codes'],10)
        return {
            'error':'no_pdb_code',
            'matches': matches
        }
