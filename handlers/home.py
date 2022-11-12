from models.sets import StructureSet
from flask import current_app

from functions.sitespecific import get_collection_colours

def home_handler():
    """
    This is a placeholder home action.

    The real one will show collections and latest structures
    """
    try:
        latest = StructureSet('website','latest').hydrate()
    except Exception as error:
        latest = None
        print (error)
    page_data = {
        'collections':current_app.data['collections']['homepage'],
        'latest':latest
    }
    return page_data