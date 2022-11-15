from typing import Dict, List
import json

import toml
import datetime
import itertools

from flask import Flask, Response, redirect


from functions.files import load_json
from functions.decorators import templated
from functions.helpers import slugify




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
    datasets = ['pdb_codes','collections','index','ordering','sets','core','listings','chains','collection_colours']
    app.data = {}
    for dataset in datasets:
        app.data[dataset] = load_json(dataset)


@app.template_filter()
def chunked_sequence(sequence):
    line_length = 60
    sequence_length = len(sequence)
    sequence_chunks = []
    i = 0
    if len(sequence) < line_length:
        i = 1
        chunked_sequence = sequence
    else:
        remainder = sequence
        while len(remainder) > line_length:
            i += 1
            sequence_chunks.append(remainder[:line_length])
            remainder = remainder[line_length:]
        if len(remainder) > 0: 
            sequence_chunks.append(remainder)
            i += 1
    j = 0
    numbers = range(10, line_length + 10, 10)
    row_labels = []
    if sequence_length > 30:
        while j < i:
            row_label = ''
            for number in numbers:
                this_number = j * line_length + number
                this_spacecount = 10 - len(str(this_number))
                if this_number < sequence_length:
                    row_label = row_label + '&nbsp;' * this_spacecount + str(this_number)
            row_labels.append(row_label)
            j += 1
    if len(row_labels) == 0:
        chunked_sequence = sequence
    else:
        labelled_chunks = [chunk for chunk in list(itertools.chain(*zip(row_labels, sequence_chunks)))]
        chunked_sequence = '<br/>'.join(labelled_chunks)
    return chunked_sequence


@app.template_filter()
def imgt_ipd_hla_parser(id):
    stem = None
    accession_id = None
    print(id)
    if id:
        if 'uniprot' in id:
            stem = None
            accession_id = None
        else:
            if 'imgt' in id:
                split_id = id.split(':')
                stem = f'{split_id[0].lower()}'
                accession_id = split_id[1]
                resource = 'IPD-IMGT/HLA'
            if 'mhc' in id:
                split_id = id.split(':')
                stem = f'{split_id[0].lower()}'
                accession_id = split_id[1]
                resource = 'IPD-MHC'
            elif 'H2-' in id or 'mouse' in id.lower():
                stem = None
                accession_id = None
    if stem and accession_id:
        if stem == 'ipd-imgt':
            url = f'https://www.ebi.ac.uk/ipd/imgt/hla/alleles/allele/?accession={accession_id}'
        else:
            url = f'https://www.ebi.ac.uk/ipd/mhc/allele/?accession={accession_id}'
        return f'<strong>{resource}</strong><br />[<a href="{url}" target="_new">{id}</a>]'
    else:
        return ''

@app.template_filter()
def slugify_this(text):
    return slugify(text)

@app.route('/')
@templated('index')
def home_handler():
    return handlers.home_handler()


@app.route('/structures/lookup/')
@app.route('/structures/lookup')
@templated('lookup')
def structure_lookup_handler():
    return handlers.structure_lookup_handler()


@app.route('/api/v1/structures/<string:pdb_code>/')
@app.route('/api/v1/structures/<string:pdb_code>')
def structure_api_handler(pdb_code):
    return handlers.structure_view_handler(pdb_code)


@app.route('/structures/view/<string:pdb_code>/')
@app.route('/structures/view/<string:pdb_code>')
@templated('structure/view')
def structure_view_handler(pdb_code):
    return handlers.structure_view_handler(pdb_code)


@app.route('/structures/browse/<string:context>/<string:set_slug>/')
@app.route('/structures/browse/<string:context>/<string:set_slug>')
@templated('shared/browse')
def structure_browse_handler(context, set_slug):
    print (context)
    print (set_slug)
    return handlers.structure_browse_handler(context, set_slug)


@app.route('/structures/collections/<string:collection_slug>/')
@app.route('/structures/collections/<string:collection_slug>')
@templated('collection')
def structure_collection_handler(collection_slug):
    return handlers.structure_collection_handler(collection_slug)



@app.get('/search')
@templated('search_page')
def search():
    return handlers.search_handler()










@app.route('/robots.txt')
def robots_txt():
    raw_response = '''
    User-agent: *
    Allow: /
    '''
    response_text = '\n'.join([line.strip() for line in raw_response.splitlines() if len(line) > 0])
    r = Response(response=response_text, status=200, mimetype="text/plain")
    r.headers["Content-Type"] = "text/plain; charset=utf-8"
    return r


@app.route('/favicon.ico')
def favicon():
    return redirect('/static/histo-32-color.png')


@app.route('/<path:path>')
@templated('404')
def error_404(path):
    return handlers.handle_404(path)
    