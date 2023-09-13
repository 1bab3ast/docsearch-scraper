import datetime

class AlgoliaSettings:
    def __init__(self):
        pass

    @staticmethod
    def get(config, levels):
        searchable_attributes = []

        # We first look for matches in the exact titles
        for level in levels:
            for selectors_key in config.selectors:
                attr_to_index = f'unordered(hierarchy_radio.{level})'
                if level in config.selectors[
                    selectors_key] and attr_to_index not in searchable_attributes:
                    searchable_attributes.extend(
                        (
                            f'unordered(hierarchy_radio_camel.{level})',
                            attr_to_index,
                        )
                    )
        # Then in the whole title hierarchy
        for level in levels:
            for selectors_key in config.selectors:
                attr_to_index = f'unordered(hierarchy.{level})'
                if level in config.selectors[
                    selectors_key] and attr_to_index not in searchable_attributes:
                    searchable_attributes.extend(
                        (f'unordered(hierarchy_camel.{level})', attr_to_index)
                    )
        for selectors_key in config.selectors:
            if 'content' in config.selectors[
                selectors_key] and 'content' not in searchable_attributes:
                searchable_attributes.append('content')

        settings = {
            'searchableAttributes': searchable_attributes,
            'attributesToRetrieve': ['hierarchy', 'content', 'anchor', 'url'],
            'attributesToHighlight': ['hierarchy', 'hierarchy_camel', 'content'],
            'attributesToSnippet': ['content:10'],
            'camelCaseAttributes': ['hierarchy', 'hierarchy_radio', 'content'],
            'attributesForFaceting': ['tags', 'no_variables', 'extra_attributes']
            + config.get_extra_facets(),
            'distinct': True,
            'attributeForDistinct': 'url',
            'customRanking': [
                'desc(weight.page_rank)',
                'desc(weight.level)',
                'asc(weight.position)',
            ],
            'ranking': [
                'words',
                'filters',
                'typo',
                'attribute',
                'proximity',
                'exact',
                'custom',
            ],
            'highlightPreTag': '<span class="algolia-docsearch-suggestion--highlight">',
            'highlightPostTag': '</span>',
            'minWordSizefor1Typo': 3,
            'minWordSizefor2Typos': 7,
            'allowTyposOnNumericTokens': False,
            'minProximity': 1,
            'ignorePlurals': True,
            'advancedSyntax': True,
            'attributeCriteriaComputedByMinProximity': True,
            'removeWordsIfNoResults': 'allOptional',
            'userData': {'lastCrawl': datetime.datetime.now().isoformat()},
        }
        # apply custom updates
        if config.custom_settings is not None:
            settings |= config.custom_settings

        return settings
