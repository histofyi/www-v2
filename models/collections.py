from functions.app import app_context

class StructureCollection():
    
    def __init__(self, collection_slug):
        self.collection_slug = collection_slug

    def get(self):
        if self.collection_slug in app_context.data['sets']:
            sets = app_context.data['sets'][self.collection_slug]
            return {
                'slug':self.collection_slug,
                'sets':sets
            }
        else:
            return {}

