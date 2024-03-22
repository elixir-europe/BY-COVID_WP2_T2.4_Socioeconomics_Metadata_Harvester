#!/usr/bin/env python3
"""Query custom DSpace API"""
import logging
from json.decoder import JSONDecodeError
import requests
from requests.exceptions import HTTPError

logger = logging.getLogger(__name__)


def get_response_from_address(address):
    '''
    Get response from HTTP/S address

    Args:
        address (str): Address to get response from

    Returns:
        response (requests.models.Response): Response from HTTP/S address
    '''
    try:
        response = requests.get(address, timeout=10)
        response.raise_for_status()
    except HTTPError as http_err:
        logger.error('HTTP error occurred: %s', http_err)
        return None
    except Exception as err:
        logger.error('Other error occurred: %s', err)
        return None
    return response


class DSpaceAPI():
    '''
    Use custom API to get handles and then oaiSources with a specific query

    Attributes:
        address (str): Address for API
        last_modified (str): Only return records modified after last_modified date
    '''
    def __init__(self, address, last_modified):
        self.address = address
        self.last_modified = last_modified

    # Solr query, e.g.:
    # https://t2-4.by-covid.bsc.es/jspui/search-items?query=((covid%20OR%20covid-19)%20OR%20pandemic)
    # &lastModified=2022-04-30
    # Returns:
    # {"responseHeader":{"query":"((covid OR covid-19) OR pandemic)","lastModified":"2022-04-30"},"response":
    # {"handles":[{"handle":"123456789/18049","collection":"CESSDA"},{"handle":"123456789/62","collection":"EUI"}]}}
    def get_handle_dict_list(self, query, collection=''):
        '''
        Get dict of DSpace Handles from DSpace API with certain Solr query and filter by selected collection

        Args:
            query (str): What to query from Solr, e.g. ((covid%%20OR%%20covid-19)OR%%20pandemic)
            collection (str): Only return handles from selected collection (endpoint)

        Returns:
            handles (dict): Handles from JSON response, e.g. [{"handle":"123456789/51989","collection":"EUI"},
                                                              {"handle":"123456789/51984","collection":"EUI"},
                                                              {"handle":"123456789/51994","collection":"EUI"}]
        '''
        full_address = self.address + 'search-items?query=' + query + '&lastModified=' + self.last_modified
        response = get_response_from_address(full_address)
        if response:
            try:
                handles = response.json()['response']['handles']
                handles_with_collection = [h for h in handles if 'collection' in h and h['collection']]
                if collection != '':
                    return [h for h in handles_with_collection if h['collection'] in collection]
                return handles
            except JSONDecodeError:
                return None
        return None

    # Handle, e.g.:
    # https://t2-4.by-covid.bsc.es/jspui/get-item?handle=123456789/18046
    # Returns:
    # [{"oaiSource":"https://datacatalogue.cessda.eu/oai-pmh/v0/oai?verb=GetRecord&metadataPrefix=oai_dc
    # &identifier=d75a712559654a5c9cac3d41770e0c2c","handle":"123456789/18046"}]
    def get_oai_source_with_handle_dict(self, handle_dict):
        '''
        Get OAI source links from DSpace API with Handle dict

        Args:
            handle_dict (dict): Handle dict from DSpace API, e.g. {"handle":"123456789/18049"}

        Returns:
            oai_source (str): Link to metadata record, e.g.
            https://datacatalogue.cessda.eu/oai-pmh/v0/oai?verb=GetRecord&metadataPrefix=oai_dc
            &identifier=422faa88aef7220e6296394570633ff247ceb219533188a9208f898204e498d0
        '''
        response = get_response_from_address(self.address + 'get-item?handle=' + handle_dict['handle'])
        if response:
            return response.json()[0]['oaiSource']
        return None

    def yield_oai_sources_with_handle_dict_list(self, handle_dict_list):
        '''
        Get and yield OAI source links from DSpace API with a list of Handle dicts

        Args:
            handle_dict_list (list): List of Handle dicts from DSpace API, e.g.
            [{"handle":"123456789/18049"},{"handle":"123456789/62"},{"handle":"123456789/20209"}]

        Returns:
            oai_source (str): Link to metadata record, e.g.
            https://datacatalogue.cessda.eu/oai-pmh/v0/oai?verb=GetRecord&metadataPrefix=oai_dc
            &identifier=422faa88aef7220e6296394570633ff247ceb219533188a9208f898204e498d0
        '''
        for handle_dict in handle_dict_list:
            response = get_response_from_address(self.address + 'get-item?handle=' + handle_dict['handle'])
            if response:
                yield response.json()[0]['oaiSource']
            else:
                yield None
