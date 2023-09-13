import os
from algoliasearch.search_client import SearchClient

app_id = os.environ.get('APPLICATION_ID', '')

api_key = os.environ.get('API_KEY', '')

app_id_prod = os.environ.get('APPLICATION_ID_PROD', '')
api_key_prod = os.environ.get('API_KEY_PROD', '')

algolia_client = SearchClient.create(app_id, api_key)
algolia_client_prod = SearchClient.create(app_id_prod, api_key_prod)


def get_facets(config):
    index = algolia_client.init_index(config)

    try:
        res = index.search('', {
            'facets': '*',
            'maxValuesPerFacet': 1000,
            'hitsPerPage': 0
        })
    except Exception:
        return None

    return res['facets'] if 'facets' in res else None


def update_docsearch_key(config, key):
    algolia_client_prod.update_api_key(
        key,
        {
            'indexes': [config],
            'description': f'docsearch frontend {config}',
            'acl': ['search'],
        },
    )


def get_docsearch_key(config):
    k = 'Not found'
    # find a key
    for key in algolia_client_prod.list_api_keys()['keys']:
        if (
            'description' in key
            and f'docsearch frontend {config}' == key['description']
            and key["acl"] == ["search"]
        ):
            k = key['value']
    return k


def add_docsearch_key(config):
    if not isinstance(config, str) or '*' in config:
        raise ValueError(f"index name : {config} is not safe")

    response = algolia_client_prod.add_api_key(
        ['search'],
        {'indexes': [config], 'description': f'docsearch frontend {config}'},
    )

    return response['key']


def delete_docsearch_key(config):
    key_to_delete = get_docsearch_key(config)
    algolia_client_prod.delete_api_key(key_to_delete)


def delete_docsearch_index(config):
    algolia_index = algolia_client_prod.init_index(config)
    algolia_index.delete()


def list_index_analytics_key(config_name):
    keys = algolia_client_prod.list_api_keys()['keys']
    return [
        key
        for key in keys
        if 'indexes' in key
        and config_name in key['indexes']
        and 'analytics' in key['acl']
    ]
