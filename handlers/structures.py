from models.sets import StructureSet
from models.structures import StructureRecord
from models.collections import StructureCollection
from actions.structures import StructureLookup
from functions.forms import request_variables


def structure_view_handler(pdb_code):
    """
    This function is the structure view handler

    """
    try:
        structure_record = StructureRecord(pdb_code).get()
        return  {
            'structure':structure_record,
            'display':True
         }
    except Exception as error:
        return {
            'error':str(error),
            'error_code':404,
            'structure':None,
            'pdb_code':pdb_code,
            'suggestions':StructureLookup(pdb_code=pdb_code).get()
        }


def structure_lookup_handler():
    """
    This function is the structure lookup handler.

    It looks up pdb codes entered into the lookup form box, or in the query string

    If a single result is found, it redirects to the structure view page for that pdb code

    If there's no single match, some suggestions are given
    """
    variables = request_variables(None, params=['pdb_code'])
    pdb_code = variables['pdb_code']
    lookup = StructureLookup(pdb_code=pdb_code).get()
    if 'exact_match' in lookup:
        return {'redirect_to':f'/structures/view/{pdb_code}'}
    else:
        return lookup 


def structure_browse_handler(context, set_slug):
    """
    This function is the structure browse handler

    """
    variables = request_variables(None, params=['page_number'])
    if not variables['page_number']:
        page = 1
    else:
        page = int(variables['page_number'])
    page_size = 25
    this_set = StructureSet(context, set_slug).hydrate(page=page, page_size=page_size)
    return {'set':this_set}


def structure_collection_handler(collection_slug):
    """
    This function is the structure collection handler

    """
    if collection_slug in ['deposited','revised','released']:
        order = 'chronology'
    else:
        order = 'count'
    collection = StructureCollection(collection_slug).get(order=order)
    return {'collection':collection,'order':order}
