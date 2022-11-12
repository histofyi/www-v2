from typing import Dict, List
import json

import toml
import datetime

from flask import Flask

from functions.files import load_json

import handlers


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
    datasets = ['pdb_codes','collections','index','ordering','sets','core','listings']
    app.data = {}
    for dataset in datasets:
        app.data[dataset] = load_json(dataset)



@app.route('/')
def home_handler():
    return handlers.home_handler()


@app.route('/structures/lookup/')
@app.route('/structures/lookup')
def structure_lookup_handler():
    return handlers.structure_lookup_handler()


@app.route('/structures/view/<string:pdb_code>/')
@app.route('/structures/view/<string:pdb_code>')
def structure_view_handler(pdb_code):
    return handlers.structure_view_handler(pdb_code)


@app.route('/structures/browse/<string:context>/<string:set_slug>/')
@app.route('/structures/browse/<string:context><string:set_slug>')
def structure_browse_handler(context, set_slug):
    return handlers.structure_browse_handler(context, set_slug)