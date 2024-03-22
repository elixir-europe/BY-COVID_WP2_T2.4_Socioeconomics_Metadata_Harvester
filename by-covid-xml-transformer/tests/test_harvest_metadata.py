#!/usr/bin/env python3
"""Tests functions in __main__"""
from io import StringIO
from lxml import etree
import pytest

from by_covid_xml_transformer.harvest_metadata import (
    handle_harvested_record,
    check_metadata_format
)
from by_covid_xml_transformer.read_write_metadata import ReadWriteMetadata



@pytest.fixture
def mock_record():
    '''
    Mock record that behaves the same way as record from oai pmh.
    '''
    class Record():
        def identifier(self):
            return 'mock_record_id'

        def element(self):
            metadata = etree.parse(StringIO("<metadata><element>data</element></metadata>"))
            return [metadata]

    return [Record(), Record(), None]


@pytest.fixture
def harvest_directory(tmpdir):
    '''
    Fixture responsible for initializing ReadWriteMetadata with temporary dir.
    '''
    return ReadWriteMetadata(tmpdir)


def test_handle_harvested_record(mock_record, harvest_directory, tmpdir):
    '''
    Tests handling of harvested record.
    '''
    endpoint_organization = "endpoint_org"
    metadata_format = "format"
    handle_harvested_record(mock_record, harvest_directory, str(tmpdir), endpoint_organization, metadata_format)

    assert (tmpdir / endpoint_organization / "mock_record_id.xml").exists()
    with open(tmpdir / endpoint_organization / "mock_record_id.xml") as file:
        content = file.read()
        assert "data" in content


def test_check_metadata_format():
    '''
    Test different cases of getting metadata format with check_metadata_format().
    '''
    # Test case 1: Metadata format found in oai_pmh_args['metadata_format_by_endpoint']
    oai_pmh_args = {
        'metadata_format_by_endpoint': {
            'endpoint1': 'oai_dc',
            'endpoint2': 'marc21'
        },
        'metadata_format': None
    }
    endpoint = 'endpoint1'
    oai_source = None
    expected_result = 'oai_dc'
    result = check_metadata_format(oai_pmh_args, endpoint, oai_source)
    assert result == expected_result

    # Test case 2: Metadata format found in oai_pmh_args['metadata_format']
    oai_pmh_args = {
        'metadata_format_by_endpoint': {},
        'metadata_format': 'oai_dc'
    }
    endpoint = 'endpoint2'
    oai_source = None
    expected_result = 'oai_dc'
    result = check_metadata_format(oai_pmh_args, endpoint, oai_source)
    assert result == expected_result

    # Test case 3: Metadata format found in oai_source
    oai_pmh_args = {
        'metadata_format_by_endpoint': {},
        'metadata_format': None
    }
    endpoint = 'endpoint2'
    oai_source = 'https://www.example.com?metadataPrefix=marc21'
    expected_result = 'marc21'
    result = check_metadata_format(oai_pmh_args, endpoint, oai_source)
    assert result == expected_result

    # Test case 4: Metadata format not found
    oai_pmh_args = {
        'metadata_format_by_endpoint': {},
        'metadata_format': None
    }
    endpoint = 'endpoint3'
    oai_source = None
    expected_result = None
    result = check_metadata_format(oai_pmh_args, endpoint, oai_source)
    assert result == expected_result
