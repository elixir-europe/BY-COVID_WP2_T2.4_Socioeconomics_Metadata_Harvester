BY-COVID XML Transformer
========================

Used for creating OmicsDI XML file containing metadata from all records harvested from OAI-PMH sources that are returned with a specific Solr query by DSpace API.

Created file(s) will then be hosted publicly and ingested by BY-COVID portal.

OmicsDI XML Validation
----------------------

GUI: https://www.omicsdi.org/validate
API: https://www.omicsdi.org/ws/#!/dataset/checkFile

With xmllint:
xmllint --noout --schema http://www.ebi.ac.uk/ebisearch/XML4dbDumps.xsd /path/to/cessda.xml
