from providers.algolia import algoliaProvider
from providers.plausible import plausibleProvider

from functions.forms import request_variables

from models.sets import StructureSetMembers

from functions.app import app_context

def search_handler():    
    empty_search = True
    variables = request_variables(None, params=['query','page_number'])
    if not variables['page_number']:
        current_page = 1
    else:
        current_page = int(variables['page_number'])
    print (variables)
    hits = 0
    pages = 0
    itemset = {'pagination':{}}
    if variables['query'] is not None:
        query = variables['query']
        algolia = algoliaProvider(app_context.config['ALGOLIA_APPLICATION_ID'], app_context.config['ALGOLIA_KEY'])
        search_results, success, errors = algolia.search('core', query, current_page)
        if 'nbHits' in search_results:
            if search_results['nbHits'] == 0:
                plausible = plausibleProvider('histo.fyi')
                plausible.empty_search(variables['query'])
                processed_search_results = []
                success = False
                errors = ['no_matching results']
                itemset['pagination'] = {
                    'total':0,
                    'current_page':0,
                    'page_count':0,
                    'page_size':25
                }
            else:
                itemset['pagination'] = {
                    'total':search_results['nbHits'],
                    'current_page':current_page,
                    'page_count':search_results['nbPages'],
                    'page_size':25,
                    'pages':range(1,search_results['nbPages'] + 1)
                }
                processed_search_results = StructureSetMembers.hydrate([result['pdb_code'] for result in search_results['hits']])
                empty_search = False
    else:
        processed_search_results = []
    return {'search_results':processed_search_results, 'variables':variables, 'query':variables['query'], 'page_number':variables['page_number'], 'empty_search':empty_search, 'set':itemset}
