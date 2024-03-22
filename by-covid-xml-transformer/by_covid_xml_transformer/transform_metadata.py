#!/usr/bin/env python3
"""Transform XML metadata"""
import logging
import os
# prettierfier is used to prettify xml but etree could probably do the same with indent when Python is 3.9+
from datetime import date
import prettierfier
from lxml import etree
from pathlib import Path
from saxonche import PySaxonProcessor
from .read_write_metadata import ReadWriteMetadata

logger = logging.getLogger(__name__)

OMICSDI_MANDATORY_FIELDS = [
    "name",
    "description"
]
OMICSDI_MANDATORY_ADDITIONAL_FIELDS = [
    "full_dataset_link",
    "repository",
]
# Currently has both publication and updated even if one is empty since it's required by By-Covid OmicsDI validator
# but technically shouldn't even have the field if it doesn't have value and then this doesn't work
OMICSDI_MANDATORY_DATES = [
    "publication",
    "updated"
]
OMICSDI_ADDITIONAL_DATES = [
    "collection_single_date",
    "collection_start_date",
    "collection_end_date"
]


def check_mandatory_fields(omicsdi_xml_string, filename):
    '''
    Checks transformed OmicsDI XML string for mandatory fields

    Args:
        omicsdi_xml_string (str): OmicsDI XML string
        filename (str): Used for logging when issues are found

    Returns:
        omicsdi_xml_string (str) or None: Preferably OmicsDI XML string
                                          but will be None if missing mandatory field values
    '''
    omicsdi_tree = etree.fromstring(omicsdi_xml_string)
    # Check that all mandatory fields have text
    for mandatory_field in OMICSDI_MANDATORY_FIELDS:
        if not omicsdi_tree.findtext(".//" + mandatory_field):
            logger.warning("Missing mandatory field %s in metadata file %s", mandatory_field, filename)
            return None
    # Check that all mandatory additional fields have text
    for mandatory_additional_field in OMICSDI_MANDATORY_ADDITIONAL_FIELDS:
        if not omicsdi_tree.findtext(".//additional_fields//field[@name='" + mandatory_additional_field + "']"):
            logger.warning("Missing mandatory additional field %s in metadata file %s ",
                           mandatory_additional_field, filename)
            return None
    # Check that at least one date has value
    all_dates_none = True
    omicsdi_tree_changed = False
    dates_to_check = OMICSDI_MANDATORY_DATES + OMICSDI_ADDITIONAL_DATES
    for date_key in dates_to_check:
        omicsdi_date = omicsdi_tree.find(".//dates//date[@type='" + date_key + "']")
        if omicsdi_date is not None:
            omicsdi_date_value = omicsdi_date.get("value")
            if omicsdi_date_value is not None:
                if date_key in OMICSDI_MANDATORY_DATES:
                    all_dates_none = False
                if len(omicsdi_date_value) == 4:
                    omicsdi_tree_changed = True
                    omicsdi_date.set("value", omicsdi_date_value + "-00-00")
                elif len(omicsdi_date_value) == 7:
                    omicsdi_tree_changed = True
                    omicsdi_date.set("value", omicsdi_date_value + "-00")
    if all_dates_none is True:
        logger.warning("Missing mandatory date (published, updated) in metadata file %s", filename)
        return None
    # Check if OmicsDI tree changed
    if omicsdi_tree_changed is True:
        omicsdi_xml_string = etree.tostring(omicsdi_tree, encoding='unicode')
    return omicsdi_xml_string


class TransformMetadata():
    '''
    Read XML metadata from file system in DC or DDI 2.5 format and transform it to OmicsDI

    Attributes:
        entries (dict): Holds the actual dataset metadata entries
        database_information (dict): Values for database section in OmicsDI according to database name
        xslt_filepaths (dict): XSLT files to use for transforming
    '''
    def __init__(self, database_information, database_name=None, xslt_filepaths=None):
        self.entries = {}
        self.database_information = database_information
        dirname = os.path.dirname(__file__)
        self.xslt_filepaths = {'codeBook': os.path.join(dirname, 'by-covid_ddi25_to_omicsdi.xslt'),
                               'dc': os.path.join(dirname, 'by-covid_dc_to_omicsdi.xslt'),
                               'oai_datacite': os.path.join(dirname, 'by-covid_datacite_to_omicsdi.xslt')}
        if database_name:
            self.entries[database_name] = []
        else:
            for database in database_information:
                self.entries[database] = []
        if xslt_filepaths:
            if xslt_filepaths['codeBook']:
                self.xslt_filepaths['codeBook'] = os.path.normpath(xslt_filepaths['codeBook'])
            if xslt_filepaths['dc']:
                self.xslt_filepaths['dc'] = os.path.normpath(xslt_filepaths['dc'])
            if xslt_filepaths['oai_datacite']:
                self.xslt_filepaths['oai_datacite'] = os.path.normpath(xslt_filepaths['oai_datacite'])

    def transform_metadata(self, harvest_directory, transform_directory_path=None, organization_subdirectory=None):
        '''
        Checks organization to see if transformation should be done (if it's given) but otherwise transforms
        all metadata.

        Args:
            transform (TransformMetadata): Previously initialized class for transformations
            harvest_directory (ReadWriteMetadata): Previously initialized class for harvesting
            transform_directory_path (str): Optional path to directory with transformed XML files
            organization_subdirectory (str): Optional value to only transform specific organization's metadata
        '''
        if transform_directory_path:
            transform_directory = ReadWriteMetadata(transform_directory_path)
        # Keep track of organizations and their entry_id since they all need to start from entry 1
        organizations = {}
        # Loop through harvested records
        for metadata in harvest_directory.read_and_yield_records(subdirectory=organization_subdirectory):
            harvested_organization = metadata['path'].split('/')[-2]
            if harvested_organization not in organizations:
                organizations[harvested_organization] = 1

            # Try to create OmicsDI for study
            omicsdi_metadata = self.transform_to_omicsdi(metadata['metadata_format'], metadata['path'],
                                                            str(organizations[harvested_organization]))
            # Add study metadata (str) to list of entries if it exists
            if omicsdi_metadata:
                self.entries[harvested_organization].append(omicsdi_metadata)
                organizations[harvested_organization] += 1
                if transform_directory_path:
                    transform_directory.write_record(metadata['name'], bytes(omicsdi_metadata, encoding="UTF-8"),
                                                    Path(transform_directory_path) / harvested_organization)
                    omicsdi_metadata = None
                    logger.info("Wrote transformed metadata with id %s to %s/%s", metadata['name'],
                                transform_directory_path, harvested_organization)

    def transform_to_omicsdi(self, metadata_format, filename, entry_id):
        '''
        Transforms XML with XSLT file by using saxon and also checks for mandatory fields before returning

        Args:
            metadata_format (str): Metadata format for selecting XSLT to use
            filename (str): Absolute or relative path to file to transform
            entry_id (str): Entry id for dataset

        Returns:
            omicsdi_xml_string (str or None): Preferably OmicsDI XML string
                                              but will be None if missing mandatory field values
        '''
        with PySaxonProcessor(license=False) as proc:
            # Create new xslt processor and set xslt
            try:
                xsltproc = proc.new_xslt30_processor()
                executable = xsltproc.compile_stylesheet(stylesheet_file=self.xslt_filepaths[metadata_format])
                executable.set_result_as_raw_value(True)

                # Set source file
                executable.set_initial_match_selection(file_name=filename)

                # Set entry_id variable
                entry_id_value = proc.make_string_value(entry_id)
                executable.set_parameter("entry_id", entry_id_value)

                omicsdi_xml_string = executable.apply_templates_returning_string()
                omicsdi_xml_string = check_mandatory_fields(omicsdi_xml_string, filename)
            except AttributeError as err:
                logger.error("Attribute error: '%s' in %s", err, filename)
                return None
            except BaseException as err:
                logger.error("Unexpected error: '%s' in %s", err, filename)
                return None
            return omicsdi_xml_string

    def prepare_final_omicsdi(self, database):
        '''
        Adds information about database to the beginning and combines all entries to create final OmicsDI XML string

        Args:
            database (str): Name of the database

        Returns:
            final_omicsdi_xml_string (str): Final OmicsDI XML string with XML declaration and UTF-8 encoding
        '''
        date_today = date.today()

        # database tag and name
        database_section = '<database><name>' + self.database_information[database]['name'] + '</name>'
        # description
        database_section += '<description>' + self.database_information[database]['description'] + '</description>'
        # release
        database_section += '<release>Release-' + date_today.strftime("%B") + '-' + str(date_today.year) + '</release>'
        # release_date
        database_section += '<release_date>' + str(date_today) + '</release_date>'
        # entry_count
        database_section += '<entry_count>' + str(len(self.entries[database])) + '</entry_count>'
        # keywords
        if self.database_information[database]['keywords']:
            database_section += '<keywords>' + self.database_information[database]['keywords'] + '</keywords>'
        # url
        if self.database_information[database]['url']:
            database_section += '<url>' + self.database_information[database]['url'] + '</url>'
        # search_url
        if self.database_information[database]['search_url']:
            database_section += '<search_url>' + self.database_information[database]['search_url'] + '</search_url>'
        # entries tag
        database_section += '<entries>\n'
        # entries
        entries_section = ''.join(self.entries[database])
        # entries and database end tags
        end_tags = '</entries></database>'

        # set self.entries[database] to None at this point to save memory
        self.entries[database] = None

        # Combine everything into one string, prettify, create etree from string
        # and then back to string with proper xml declaration and encoding
        omicsdi_metadata = ''.join([database_section, entries_section, end_tags])
        entries_section = None
        omicsdi_metadata = prettierfier.prettify_xml(omicsdi_metadata, indent=2, debug=False)
        omicsdi_metadata = etree.fromstring(omicsdi_metadata)
        omicsdi_metadata = etree.tostring(omicsdi_metadata, xml_declaration=True, encoding='utf8')
        return omicsdi_metadata

    def create_final_omicsdi_xml(self, omicsdi_directory_path, databases):
        '''
        Creates a final OmicsDI XML that can then be moved to a public directory
        to be used in BY-COVID portal

        Args:
            transform (TransformMetadata): Previously initialized class for transformations
            omicsdi_directory_path (str): Path to directory with final OmicsDI XML file(s)
            databases (list): List of databases to create final OmicsDI XML for
        '''
        # Create directory for final OmicsDI xml files
        omicsdi_directory = ReadWriteMetadata(omicsdi_directory_path)
        # Create and write final OmicsDI xml files for each database
        for database in databases:
            final_omicsdi_content = self.prepare_final_omicsdi(database)
            omicsdi_directory.write_record(database + '.xml', final_omicsdi_content)
            logger.info("Wrote final OmicsDI XML file for database %s to %s/%s.xml", database, omicsdi_directory_path,
                        database)
