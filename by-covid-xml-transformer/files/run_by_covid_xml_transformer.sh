#!/bin/bash
rm /home/apps/harvested_xml_files/**/*.xml
# Delete transformed also if saving them
cd /home/apps/by-covid-xml-transformer
/home/apps/by-covid-xml-transformer-env/bin/python3 -m by_covid_xml_transformer
