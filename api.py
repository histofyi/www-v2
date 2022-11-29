from flask import Blueprint, jsonify

import handlers

api_handlers = Blueprint('api_handlers', __name__)



@api_handlers.route('/')
def api_route():
    return {'hello':'world'}


@api_handlers.route('/structures/<string:pdb_code>/')
@api_handlers.route('/structures/<string:pdb_code>')
def structures_route(pdb_code):
    return handlers.structure_view_handler(pdb_code)


@api_handlers.route('/search')
def search_route():
    return handlers.search_handler()