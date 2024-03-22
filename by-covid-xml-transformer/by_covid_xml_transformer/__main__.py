#!/usr/bin/env python3
"""Harvest OAI-PMH endpoint(s) and read/write/transform metadata"""
import sys
import logging
from pathlib import Path
import configargparse
import yaml
from py12flogging import log_formatter

from .read_write_metadata import ReadWriteMetadata
from .transform_metadata import TransformMetadata
from .harvest_metadata import harvest_metadata

log_formatter.setup_app_logging('by_covid_xml_transformer', loglevel=logging.WARNING)

logger = logging.getLogger(__name__)

def parse_all_args():
    '''
    Parse arguments from environment variables, configuration files and/or command line parameters

    Returns:
        options (argparse.Namespace): Parsed arguments
    '''
    parser = configargparse.ArgParser(config_file_parser_class=configargparse.ConfigparserConfigFileParser,
                                      default_config_files=['configuration.yaml'])
    parser.add('-p', '--print_current_config', help='Show keys and values added to namespace and where they come from',
               action='store_true')
    parser.add('-c', '--config', is_config_file=True, help='Config file path')
    parser.add('-v', help='verbose', action='store_true')
    dspace_api_group = parser.add_argument_group("DSpace API", "Settings related to DSpace API")
    dspace_api_group.add('-a', '--dspace_api_base_address', help='Base address of DSpace API',
                         env_var='XML_TRANSFORMER_DSPACE_API_ADDRESS')
    dspace_api_group.add('-l', '--dspace_api_last_modified', help='Last modified date for DSpace API',
                         env_var='XML_TRANSFORMER_DSPACE_API_LAST_MODIFIED')
    dspace_api_group.add('-q', '--dspace_api_query', help='Query for DSpace API',
                         env_var='XML_TRANSFORMER_DSPACE_API_QUERY')
    dspace_api_group.add('-qe', '--dspace_api_query_by_endpoint',
                         help='Query for DSpace API by endpoint',
                         env_var='XML_TRANSFORMER_DSPACE_API_QUERY_BY_ENDPOINT', type=yaml.safe_load)
    dspace_api_group.add('-ce', '--dspace_api_collection_by_endpoint',
                         help='Collection for DSpace API by endpoint',
                         env_var='XML_TRANSFORMER_DSPACE_API_COLLECTION_BY_ENDPOINT', type=yaml.safe_load)
    directory_path_group = parser.add_argument_group("Directory paths", "Set paths for writing/reading files")
    directory_path_group.add('-hd', '--harvest_directory_path',
                             help='Path to directory where to write/read harvested metadata files',
                             env_var='XML_TRANSFORMER_HARVEST_DIRECTORY_PATH')
    directory_path_group.add('-td', '--transform_directory_path',
                             help='Path to directory where to write/read transformed metadata files',
                             env_var='XML_TRANSFORMER_TRANSFORM_DIRECTORY_PATH')
    directory_path_group.add('-od', '--omicsdi_directory_path',
                             help='Path to directory where to write final OmicsDI file',
                             env_var='XML_TRANSFORMER_OMICSDI_DIRECTORY_PATH')
    oai_pmh_group = parser.add_argument_group("Metadata format",
                                              "Set metadata format globally and/or by OAI-PMH endpoint")
    oai_pmh_group.add('-f', '--oai_pmh_metadata_format', help='Metadata format to harvest',
                      env_var='XML_TRANSFORMER_OAI_PMH_METADATA_FORMAT')
    oai_pmh_group.add('-fe', '--oai_pmh_metadata_format_by_endpoint',
                      help='Metadata format to harvest by endpoint',
                      env_var='XML_TRANSFORMER_OAI_PMH_METADATA_FORMAT_BY_ENDPOINT', type=yaml.safe_load)
    oai_pmh_group.add('-e', '--oai_pmh_exclusion_list',
                      help='Identifiers to exclude from entries',
                      env_var='XML_TRANSFORMER_OAI_PMH_EXCLUSION_LIST', action="append")
    transform_metadata_group = parser.add_argument_group("OmicsDI", "Settings related to OmicsDI")
    transform_metadata_group.add('-x', '--xslt_paths',
                                 help='Paths to XSLT files for transforming other formats to OmicsDI',
                                 env_var='XML_TRANSFORMER_XSLT_PATHS', type=yaml.safe_load)
    transform_metadata_group.add('-d', '--database_information', help='Information for databases',
                                 env_var='XML_TRANSFORMER_DATABASE_INFORMATION', type=yaml.safe_load)
    parser.add('-r', '--read_only', help='Read from existing metadata files only',
               env_var='XML_TRANSFORMER_READ_ONLY', action='store_true')
    options = parser.parse_args()

    if options.print_current_config:
        print(options)
        print("----------")
        print(parser.format_values())
        sys.exit(0)

    return options


def main():
    '''
    Get metadata from DSpace API, then OAI-PMH endpoint(s) and write all metadata to filesystem in OmicsDI format

    Returns:
        0 (int): Returns 0 on success
    '''
    args = parse_all_args()
    harvest_directory = ReadWriteMetadata(args.harvest_directory_path)

    # Harvest studies according to Solr query result from DSpace API (Handles) if not read only
    if not args.read_only:
        oai_pmh_args = {'metadata_format': args.oai_pmh_metadata_format,
                        'metadata_format_by_endpoint': args.oai_pmh_metadata_format_by_endpoint,
                        'exclusion_list': args.oai_pmh_exclusion_list}
        dspace_api_args = {'address': args.dspace_api_base_address,
                           'last_modified': args.dspace_api_last_modified,
                           'query': args.dspace_api_query,
                           'query_by_endpoint': args.dspace_api_query_by_endpoint,
                           'collection_by_endpoint': args.dspace_api_collection_by_endpoint}
        # Add default query for endpoints that have metadata format set but no query
        for query_endpoint in oai_pmh_args['metadata_format_by_endpoint'].keys():
            if query_endpoint not in dspace_api_args['query_by_endpoint'].keys():
                dspace_api_args['query_by_endpoint'][query_endpoint] = dspace_api_args['query']
        # Add default metadata format for endpoints that have query set but no metadata format
        for query_endpoint in dspace_api_args['query_by_endpoint'].keys():
            if query_endpoint not in oai_pmh_args['metadata_format_by_endpoint'].keys():
                oai_pmh_args['metadata_format_by_endpoint'][query_endpoint] = oai_pmh_args['metadata_format']
        harvest_metadata(harvest_directory, args.harvest_directory_path, oai_pmh_args, dspace_api_args)

    # Get a list of subdirectories in harvest directory as strings
    subdirs = [str(x).rsplit('/', maxsplit=1)[-1] for x in Path(args.harvest_directory_path).iterdir() if x.is_dir()]

    for organization_subdirectory in subdirs:
        transform = TransformMetadata(args.database_information, organization_subdirectory, args.xslt_paths)
        transform.transform_metadata(harvest_directory, args.transform_directory_path, organization_subdirectory)
        transform.create_final_omicsdi_xml(args.omicsdi_directory_path, [organization_subdirectory])
        transform = None

    return 0


if __name__ == '__main__':
    sys.exit(main())
