#!/bin/bash
cd /home/apps/temp_omicsdi_xml_files
xmllint --noout --schema http://www.ebi.ac.uk/ebisearch/XML4dbDumps.xsd cessda.xml && mv cessda.xml /shared/omicsdi_xml_files/cessda.xml
xmllint --noout --schema http://www.ebi.ac.uk/ebisearch/XML4dbDumps.xsd eui.xml && mv eui.xml /shared/omicsdi_xml_files/eui.xml
