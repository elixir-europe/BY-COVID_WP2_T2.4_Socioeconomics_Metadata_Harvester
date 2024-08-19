#!/usr/bin/env python3
"""Get metadata from OAI-PMH endpoint"""
import logging
import re
from urllib.error import HTTPError
from oaipmh.client import Client
from oaipmh.metadata import MetadataRegistry, MetadataReader, oai_dc_reader
from oaipmh.error import IdDoesNotExistError

logger = logging.getLogger(__name__)


# oaipmh's MetadataReader doesn't save attributes by default at all
# https://github.com/infrae/pyoai/blob/master/src/oaipmh/metadata.py#L59
# Saving attribute can be done with something like:
# 'producer_abbr_en':  ('text', 'ddi:codeBook/ddi:docDscr/ddi:citation/ddi:prodStmt/ddi:producer[@xml:lang="en"]/@abbr')
oai_ddi25_reader = MetadataReader(
    fields = {
        'title':        ('textList', 'ddi:codeBook/ddi:stdyDscr/ddi:citation/ddi:titlStmt/ddi:titl/text()'),
        'producer':     ('textList', 'ddi:codeBook/ddi:docDscr/ddi:citation/ddi:prodStmt/ddi:producer/text()')
        # 'creator':     ('textList', 'oai_dc:dc/dc:creator/text()'),
        # 'subject':     ('textList', 'oai_dc:dc/dc:subject/text()'),
        # 'description': ('textList', 'oai_dc:dc/dc:description/text()'),
        # 'publisher':   ('textList', 'oai_dc:dc/dc:publisher/text()'),
        # 'contributor': ('textList', 'oai_dc:dc/dc:contributor/text()'),
        # 'date':        ('textList', 'oai_dc:dc/dc:date/text()'),
        # 'type':        ('textList', 'oai_dc:dc/dc:type/text()'),
        # 'format':      ('textList', 'oai_dc:dc/dc:format/text()'),
        # 'identifier':  ('textList', 'oai_dc:dc/dc:identifier/text()'),
        # 'source':      ('textList', 'oai_dc:dc/dc:source/text()'),
        # 'language':    ('textList', 'oai_dc:dc/dc:language/text()'),
        # 'relation':    ('textList', 'oai_dc:dc/dc:relation/text()'),
        # 'coverage':    ('textList', 'oai_dc:dc/dc:coverage/text()'),
        # 'rights':      ('textList', 'oai_dc:dc/dc:rights/text()')
    },
    namespaces = {
        'ddi': 'ddi:codebook:2_5'
    }
)

oai_datacite_reader = MetadataReader(
    fields = {
        'title':        ('textList', 'oai:oai_datacite/oai:payload/kernel:resource/kernel:titles/kernel:title/text()'),
        # 'producer':    ('textList', 'ddi:codeBook/ddi:docDscr/ddi:citation/ddi:prodStmt/ddi:producer/text()')
        # 'creator':     ('textList', 'oai_dc:dc/dc:creator/text()'),
        # 'subject':     ('textList', 'oai_dc:dc/dc:subject/text()'),
        # 'description': ('textList', 'oai_dc:dc/dc:description/text()'),
        # 'publisher':   ('textList', 'oai_dc:dc/dc:publisher/text()'),
        # 'contributor': ('textList', 'oai_dc:dc/dc:contributor/text()'),
        # 'date':        ('textList', 'oai_dc:dc/dc:date/text()'),
        # 'type':        ('textList', 'oai_dc:dc/dc:type/text()'),
        # 'format':      ('textList', 'oai_dc:dc/dc:format/text()'),
        # 'identifier':  ('textList', 'oai_dc:dc/dc:identifier/text()'),
        # 'source':      ('textList', 'oai_dc:dc/dc:source/text()'),
        # 'language':    ('textList', 'oai_dc:dc/dc:language/text()'),
        # 'relation':    ('textList', 'oai_dc:dc/dc:relation/text()'),
        # 'coverage':    ('textList', 'oai_dc:dc/dc:coverage/text()'),
        # 'rights':      ('textList', 'oai_dc:dc/dc:rights/text()')
    },
    namespaces = {
        "oai": "http://schema.datacite.org/oai/oai-1.1/",
        "kernel": "http://datacite.org/schema/kernel-4"
    }
)


class OaiPmh():
    '''
    Get metadata from OAI-PMH endpoint

    Attributes:
        metadata_format (str): Metadata format to use when retrieving metadata
        clients (dict): Clients for each encountered endpoint
    '''
    def __init__(self, metadata_format=None):
        self.metadata_format = metadata_format
        self.clients = {}

    def set_client(self, endpoint, metadata_format=None):
        '''
        Sets endpoint specific OAI-PMH client that has registry with reader set

        Args:
            endpoint (str): OAI-PMH endpoint that will be saved in clients dict
            metadata_format (str): Decides which reader to use for metadata

        Returns:
            Client (oaipmh.client.Client): Returns the endpoint specific OAI-PMH client
        '''
        registry = MetadataRegistry()
        if metadata_format in ['oai_dc']:
            registry.registerReader('oai_dc', oai_dc_reader)
        elif metadata_format in ['oai_ddi25']:
            registry.registerReader('oai_ddi25', oai_ddi25_reader)
        elif metadata_format in ['oai_datacite']:
            registry.registerReader('oai_datacite', oai_datacite_reader)
        else:
            logger.error("Unrecognized metadata format: %s", metadata_format)
            return None
        self.clients[endpoint] = Client(endpoint, registry)
        return self.clients[endpoint]

    def get_client(self, endpoint, metadata_format=None):
        '''
        Gets endpoint specific OAI-PMH client that has registry with reader set

        Args:
            endpoint (str): OAI-PMH endpoint to use for client (existing or new)
            metadata_format (str): Decides which reader to use for metadata if setting new client

        Returns:
            Client (oaipmh.client.Client): Returns the endpoint specific OAI-PMH client
        '''
        if endpoint in self.clients:
            return self.clients[endpoint]
        return self.set_client(endpoint, metadata_format)

    def get_record(self, _oai_source=None, _prefix=None, endpoint=None, _id=None):
        '''
        Gets metadata record from OAI-PMH client

        Args:
            _oai_source (str): Link to metadata record to harvest (not required if endpoint and _id have values)
            _prefix (str): Highest priority for metadata format to use in harvesting if set
            endpoint (str): Which endpoint's client to use (not required if part of _oai_source)
            _id (str): ID of the record to harvest (not required if part of _oai_source)

        Returns:
            record (tuple): Contains Header, Metadata and About (not yet implemented in oaipmh)
        '''
        # Order for used metadata format (prefix):
        # 1. _prefix
        # 2. self.metadata_format
        # 3. _oai_source
        if _oai_source is None:
            if endpoint is None or _id is None:
                logger.error("Either _oai_source or endpoint & _id are required")
                return [None, None, None]
            if _prefix is None and self.metadata_format is None:
                logger.error("Either _prefix or self.metadata_format are required")
                return [None, None, None]
        else:
            endpoint = re.search(r'.+?(?=\?verb)', _oai_source, re.IGNORECASE).group()
            _id = re.search(r'identifier=([^&]+)', _oai_source, re.IGNORECASE).group(1)
            if _prefix is None and self.metadata_format is None:
                _prefix = re.search(r'metadataPrefix=([^&]+)', _oai_source, re.IGNORECASE).group(1)
        if _prefix is None:
            _prefix = self.metadata_format

        client = self.get_client(endpoint, _prefix)
        try:
            record = client.getRecord(metadataPrefix=_prefix, identifier=_id)
        except HTTPError:
            record = [None, None, None]
        except IdDoesNotExistError:
            logger.error(f"Identifier does not exist: {_id}")
            record = [None, None, None]
        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            record = [None, None, None]
        return record

    def get_records(self, endpoint, metadata_prefix=None):
        '''
        Get and yield all metadata records from endpoint

        Args:
            endpoint (str): Which endpoint's client to use
            metadata_format (str): Which metadata format to use if not using default

        Returns:
            record (tuple): Contains Header, Metadata and About (not yet implemented in oaipmh)
        '''
        client = self.get_client(endpoint)

        metadata_prefix = metadata_prefix if metadata_prefix else self.metadata_format

        for record in client.listRecords(metadataPrefix=metadata_prefix):
            yield record
