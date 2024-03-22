import os
from distutils import dir_util
import pytest
from lxml import etree
from freezegun import freeze_time

from by_covid_xml_transformer.read_write_metadata import ReadWriteMetadata
from by_covid_xml_transformer.transform_metadata import TransformMetadata, check_mandatory_fields

@pytest.fixture(name="rw_class")
def fixture_rw_class(tmpdir):
    '''
    Fixture responsible for initializing ReadWriteMetadata with temporary dir.
    '''
    rw_directory = ReadWriteMetadata(tmpdir)
    return rw_directory

@pytest.fixture(name="data_dir")
def fixture_data_dir(tmpdir, request):
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

def test_transform_to_omicsdi(data_dir, rw_class, tmpdir):
    '''
    Tests successfully creating OmicsDI XML from DDI-C 2.5.
    '''
    database_information = {
        "test": {"name": "TEST Catalogue",
                 "description": "TEST catalogue's description",
                 "keywords": "social sciences,humanities",
                 "url": "https://example.com",
                 "search_url": ""}
    }
    transform = TransformMetadata(database_information)
    omicsdi_metadata = transform.transform_to_omicsdi(
        'codeBook',
        str(tmpdir + '/7f1f8f6fdf7312bbb37e638ee2468fa243dc9aab9a21597a6121cf833f0c281f.xml'),
        '1'
    )
    rw_class.write_record('test.xml', bytes(omicsdi_metadata, encoding="UTF-8"))
    written_file = tmpdir.join('test.xml')
    assert written_file.read() == data_dir.join('omicsdi.xml').read()

@pytest.fixture(name="omicsdi_xml_one")
def fixture_omicsdi_xml_one(data_dir):
    '''
    Fixture responsible for OmicsDI test XML file.
    '''
    omicsdi_xml = data_dir.join('f893ad66cc1ae204dd9a06bc7f072a46284c4ddee43cf08d958080d10373a34d.xml')
    return omicsdi_xml

@pytest.fixture(name="omicsdi_xml_two")
def fixture_omicsdi_xml_two(data_dir):
    '''
    Fixture responsible for OmicsDI test XML file.
    '''
    omicsdi_xml = data_dir.join('aa1002ac7b26ebe14a002497f81a40f677ea9d00af7cd3408a56910428635592.xml')
    return omicsdi_xml

@pytest.fixture(name="final_omicsdi_xml")
def fixture_final_omicsdi_xml(data_dir):
    '''
    Fixture responsible for final OmicsDI XML file.
    '''
    omicsdi_xml = data_dir.join('final_omicsdi.xml')
    return omicsdi_xml

@freeze_time("2022-10-13")
def test_prepare_final_omicsdi(omicsdi_xml_one, omicsdi_xml_two, final_omicsdi_xml, rw_class, tmpdir):
    '''
    Tests successfully creating OmicsDI content for a database.
    '''
    database_information = {
        "test": {"name": "TEST Catalogue",
                 "description": "TEST catalogue's description",
                 "keywords": "social sciences,humanities",
                 "url": "https://example.com",
                 "search_url": ""}
    }
    transform = TransformMetadata(database_information)
    transform.entries['test'].append(omicsdi_xml_one.read())
    transform.entries['test'].append(omicsdi_xml_two.read())
    final_omicsdi_content = transform.prepare_final_omicsdi('test')
    rw_class.write_record('test.xml', final_omicsdi_content)
    written_file = tmpdir.join('test.xml')
    assert written_file.read() == final_omicsdi_xml.read()
