#!/bin/sh
sed -i '/<\/Host>/i\        <Context docBase="/shared/omicsdi_xml_files" path="/xmls" \/>' /usr/local/tomcat/conf/server.xml
