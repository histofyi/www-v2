from models.sets import StructureSet
from models.structures import StructureRecord
from actions.structures import StructureLookup
from functions.forms import request_variables

def structure_view_handler(pdb_code):
    """
    This function is the structure view handler

    """
    try:
        structure_record = StructureRecord(pdb_code).get()
        return  {
            'structure_record':structure_record
         }
    except Exception as error:
        return {
            'error':str(error),
            'error_code':404,
            'structure_record':None,
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
    variables = request_variables(None, params=['page'])
    if not variables['page']:
        page = 1
    else:
        page = variables['page']
    page_size = 25
    this_set = StructureSet(context, set_slug).hydrate(page=page, page_size=page_size)
    return this_set
