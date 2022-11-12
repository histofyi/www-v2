from typing import List, Dict, Tuple, Union
from flask import current_app

class StructureSetMembers():

    def hydrate(members, depth='listings'):
        if depth == 'listings':
            hydration = current_app.data['listings']
        else:
            hydration = current_app.data['core']
        return [hydration[pdb_code] for pdb_code in members]

  
class StructureSet():

    def __init__(self, context:str, slug:str):
        self.errors = []
        self.context = context
        self.slug = slug
        self.sets = current_app.data['sets']
        if context in self.sets:
            if slug in self.sets[context]:
                self.set = self.sets[context][slug]
            else:
                self.set = None
                raise Exception('Set not found error. No set named "{slug}" could be found within the contect "{context}"'.format(slug=slug,context=context))
        else:
            self.set = None
            raise Exception('Context not found error. No context named "{context}" could be found'.format(context=context))


    def paginate(self, page=None, page_size=None):
        pass


    def get(self, page=None, page_size=None):
        if not page_size:
            return self.set
        else:
            return self.paginate(page, page_size)

    
    def hydrate(self, page=1, page_size=25, depth='listings'):
        self.get()
        hydrated_set = {}
        for key in self.set:
            hydrated_set[key] = self.set[key]
        hydrated_set['members'] = StructureSetMembers.hydrate(self.set['members'])
        return hydrated_set




