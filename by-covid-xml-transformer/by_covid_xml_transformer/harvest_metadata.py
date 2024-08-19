#!/usr/bin/env python3
"""Help with harvesting metadata from OAI-PMH"""
import logging
import re
from pathlib import Path
from lxml import etree
from .dspace_api import DSpaceAPI
from .oai_pmh import OaiPmh

logger = logging.getLogger(__name__)

def handle_harvested_record(record, harvest_directory, harvest_directory_path, endpoint_organization, metadata_format):
    '''
    Creates a final OmicsDI XML that can then be moved to a public directory
    to be used in BY-COVID portal

    Args:
        record (tuple): Contains Header, Metadata and About (not yet implemented in oaipmh)
        harvest_directory (ReadWriteMetadata): Previously initialized class for harvesting
        harvest_directory_path (str): Path to directory with harvested XML files
        endpoint_organization (str): Endpoint organization derived from endpoint
        metadata_format (str): Metadata format used when harvesting
    '''
    record_id = record[0].identifier()
    metadata_tree = harvest_directory.strip_html_from_xml_string(
        etree.tostring(record[1].element()[0], encoding='unicode'), record_id, endpoint_organization, metadata_format)
    if metadata_tree is not None:
        file_content = etree.tostring(metadata_tree, xml_declaration=True, encoding='utf8', pretty_print=True)
        # file_content = etree.tostring(record[1].element()[0], encoding='unicode', pretty_print=True)
        harvest_directory.write_record(record_id + '.xml', file_content,
                                       Path(harvest_directory_path) / endpoint_organization)
        logger.info("Wrote harvested metadata with id %s to %s/%s", record_id, harvest_directory_path,
                    endpoint_organization)


def check_metadata_format(oai_pmh_args, endpoint, oai_source=None):
    '''
    Returns metadata format for endpoint

    Args:
        oai_pmh_args (dict): Args for OAI-PMH
        endpoint (str): Link to the endpoint
        oai_source (str): Link to an OAI-PMH record that includes metadataPrefix
    '''
    if oai_pmh_args['metadata_format_by_endpoint'] or oai_pmh_args['metadata_format']:
        if oai_pmh_args['metadata_format_by_endpoint']:
            if oai_pmh_args['metadata_format_by_endpoint'][endpoint]:
                metadata_format = oai_pmh_args['metadata_format_by_endpoint'][endpoint]
        else:
            metadata_format = oai_pmh_args['metadata_format']
    elif oai_source:
        metadata_format = re.search(r'metadataPrefix=([^&]+)', oai_source, re.IGNORECASE).group(1)
    else:
        logger.warning("Couldn't resolve metadata format for endpoint %s", endpoint)
        return None
    return metadata_format


def harvest_metadata(harvest_directory, harvest_directory_path, oai_pmh_args, dspace_api_args):
    '''
    Creates a final OmicsDI XML that can then be moved to a public directory
    to be used in BY-COVID portal

    Args:
        harvest_directory (ReadWriteMetadata): Previously initialized class for harvesting
        harvest_directory_path (str): Path to directory with harvested XML files
        oai_pmh_args (dict): Args for OAI-PMH
        dspace_api_args (dict): Args for DSpace API
    '''
    oai_pmh = OaiPmh(oai_pmh_args['metadata_format']) if oai_pmh_args['metadata_format'] else OaiPmh()
    dspace_api = DSpaceAPI(dspace_api_args['address'], dspace_api_args['last_modified'])

    # For debugging actually excluded records
    # excluded_records = []

    # Loop queries by endpoint
    for query_endpoint, query in dspace_api_args['query_by_endpoint'].items():
        collection = dspace_api_args['collection_by_endpoint'][query_endpoint]
        logger.info("Querying for endpoint %s with query %s and collection %s", query_endpoint, query, collection)
        # Solr query
        handle_dict_list = dspace_api.get_handle_dict_list(query, collection)

        # For testing purposes
        # CDC:
        #   f893ad66cc1ae204dd9a06bc7f072a46284c4ddee43cf08d958080d10373a34d has nothing special
        #   422faa88aef7220e6296394570633ff247ceb219533188a9208f898204e498d0 has escaped HTML etc.
        #   4f1dfb1ab4e81eb82f0ea220cc3cc4ff863e6b42c782c1356ed12913d78fbac7 has extremely long abstract
        #   ead3c65e58831fdb38dce8f3c32ed576e8d5968412add2f50150aae031975afd doesn't have English values
        # in ['https://datacatalogue.cessda.eu/oai-pmh/v0/oai?verb=GetRecord&metadataPrefix=oai_dc&identifier=']:
        #
        # EUI:
        #   oai:covid19data.eui.eu:t9afe-gvy90 has nothing special
        # in ['https://covid19data.eui.eu/oai2d?verb=GetRecord&metadataPrefix=oai_datacite&identifier=']:

        # Process each Handle
        if handle_dict_list:
            for oai_source in dspace_api.yield_oai_sources_with_handle_dict_list(handle_dict_list):
                logger.info("Harvesting %s", oai_source)
                metadata_format = check_metadata_format(oai_pmh_args, query_endpoint, oai_source)
                record = oai_pmh.get_record(oai_source, metadata_format)
                # record[0] is Header - identifier(), datestamp(), setSpec(), isDeleted()
                # record[1] is Metadata - element(), getMap(), getField(name)
                # record[2] is About - not yet implemented
                # For record[1] (Metadata class object), element() contains the whole metadata element as it is and
                # element()[0] is the actual metadata (as lxml.etree._Element)
                # TODO Handle deleted records (record[1] is None)
                if record[1] is not None:
                    if (oai_pmh_args['exclusion_list']
                        and record[0].identifier() in oai_pmh_args.get('exclusion_list', [])):
                        logger.info("Identifier %s found in exclusion list and will not be handled further",
                                    record[0].identifier())

                        # For debugging actually excluded records
                        # excluded_records.append(record[0].identifier())
                    else:
                        handle_harvested_record(record, harvest_directory, harvest_directory_path,
                                                query_endpoint.split('.')[-2], metadata_format)
                else:
                    logger.info("Record from %s has no metadata and will not be handled further", oai_source)
        else:
            logger.warning("Handle dict list empty for endpoint %s with query %s and collection %s",
                           query_endpoint, query, collection)
    # TODO If we get a bunch of smaller endpoints that don't need specific query
    # then do a generic query here for all results but disregard the ones that we already have

    # For debugging actually excluded records
    # for record in excluded_records:
    #     print("'" + record + "',")

    logger.info("Harvesting finished")
