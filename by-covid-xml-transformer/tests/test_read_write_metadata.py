#!/usr/bin/env python3
"""Tests functions of class ReadWriteMetadata"""
from distutils import dir_util
import os
import pytest
from lxml import etree

from by_covid_xml_transformer.read_write_metadata import ReadWriteMetadata

@pytest.fixture
def rw_class(tmpdir):
    '''
    Fixture responsible for initializing ReadWriteMetadata with temporary dir.
    '''
    rw_directory = ReadWriteMetadata(tmpdir)
    return rw_directory

@pytest.fixture
def data_dir(tmpdir, request):
    '''
    Fixture responsible for searching a folder with the same name of test
    module and, if available, moving all contents to a temporary directory so
    tests can use them freely.
    '''
    filename = request.module.__file__
    test_dir, _ = os.path.splitext(filename)

    if os.path.isdir(test_dir):
        dir_util.copy_tree(test_dir, str(tmpdir))

    return tmpdir

@pytest.fixture
def ddi_xml(data_dir):
    '''
    Fixture responsible for test XML file.
    '''
    ddi_xml = data_dir.join('f893ad66cc1ae204dd9a06bc7f072a46284c4ddee43cf08d958080d10373a34d.xml')
    return ddi_xml

def test_write_record_success(rw_class, ddi_xml, tmpdir):
    '''
    Tests successfully writing an XML file.
    '''
    filename = 'ddi25.xml'
    rw_class.write_record(filename, str.encode(ddi_xml.read()))
    written_file = tmpdir.join(filename)
    assert written_file.read() == ddi_xml.read()

def test_read_and_yield_records_success(data_dir, rw_class, ddi_xml):
    '''
    Tests successfully reading a directory of XML files.
    '''
    filename = 'f893ad66cc1ae204dd9a06bc7f072a46284c4ddee43cf08d958080d10373a34d.xml'
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(ddi_xml, parser)
    file_content = etree.tostring(tree, encoding='unicode', pretty_print=True)
    for metadata in rw_class.read_and_yield_records(data_dir, None, True):
        assert metadata['name'] == filename and metadata['content'] == file_content

def test_strip_html_from_xml_string(rw_class, ddi_xml):
    '''
    Tests successfully stripping HTML from XML file.
    '''
    parser = etree.XMLParser(encoding='utf-8')
    with open(ddi_xml, encoding='utf-8') as test_xml_open:
        test_xml_open.readline()
        test_xml_without_declaration = test_xml_open.read()
    test_xml_content_tree = etree.fromstring(test_xml_without_declaration, parser)
    metadata_tree = rw_class.strip_html_from_xml_string(test_xml_without_declaration, "1", "test org", "oai_ddi25")
    assert etree.tostring(metadata_tree) == etree.tostring(test_xml_content_tree)
