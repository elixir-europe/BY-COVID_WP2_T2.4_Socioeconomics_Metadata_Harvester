Installing BY-COVID XML Transformer
-----------------------------------

1. Change to repository directory

   cd by_covid_xml_transformer

2. Create virtualenv

   python3 -m venv ../by_covid_xml_transformer-env

3. Activate virtualenv

   source ../by_covid_xml_transformer-env/bin/activate

4. Install requirements

   pip install -r requirements.txt

5. Install by_covid_xml_transformer

   pip install .

Setting up cronjob for BY-COVID XML transformer
-----------------------------------------------

Create script for running BY-COVID XML transformer and moving XML after validation:

1. nano run_by_covid_xml_transformer.sh

::

   #!/bin/bash
   rm /your/path/to/by-covid/harvested_xml_files/**/*.xml
   # Delete transformed also if saving them
   #rm /your/path/to/by-covid/transformed_xml_files/**/*.xml
   cd /your/path/to/by-covid/by-covid_xml_transformer
   /your/path/to/by-covid-xml-transformer-env/bin/python3 -m by_covid_xml_transformer

2. nano validate_and_move_xmls.sh

::

   #!/bin/bash
   cd /your/path/to/by-covid/temp_omicsdi_xml_files
   mkdir -p ../omicsdi_xml_files
   xmllint --noout --schema http://www.ebi.ac.uk/ebisearch/XML4dbDumps.xsd cessda.xml && mv cessda.xml ../omicsdi_xml_files/cessda.xml
   xmllint --noout --schema http://www.ebi.ac.uk/ebisearch/XML4dbDumps.xsd eui.xml && mv eui.xml ../omicsdi_xml_files/eui.xml


3. chmod 775 run_by-covid_xml_transformer.sh
4. chmod 775 validate_and_move_xmls.sh
5. mkdir /your/path/to/by-covid/logs
6. crontab -e

::

   0 3 * * * cd /your/path/to/by-covid && ./run_by_covid_xml_transformer.sh > logs/`date +\%Y\%m\%d\%H\%M\%S`-by-covid-xml-transformer-cron.log 2>&1 && ./validate_and_move_xmls.sh > logs/`date +\%Y\%m\%d\%H\%M\%S`-xml-validation-cron.log 2>&1

Installation commands example from BY-COVID server
--------------------------------------------------

| sudo groupadd apps
| sudo useradd apps --system -g apps -m -s /bin/bash
| sudo usermod -a -G apps user
| sudo apt-get install python3 python3-dev python3-pip python3.8-venv libxml2-utils
| cd /home/user
| mv by-covid_xml_transformer /home/apps/
| cd /home/apps
| sudo chown -R apps:apps by-covid_xml_transformer
| sudo su apps
| python3 -m venv by-covid_xml_transformer-env
| source by-covid_xml_transformer-env/bin/activate
| cd by-covid_xml_transformer
| pip install -r requirements.txt
| pip install .
| cp configuration.yaml.dist configuration.yaml
| nano configuration.yaml
| cd /home/apps
| mkdir logs
| nano run_by-covid_xml_transformer.sh
| chmod 750 run_by-covid_xml_transformer.sh
| crontab -e

Running tests
-------------

1. Change to repository directory

   cd by_covid_xml_transformer

2. Create virtualenv

   python3 -m venv ../by_covid_xml_transformer-env

3. Activate virtualenv

   source ../by_covid_xml_transformer-env/bin/activate

4. Install dev requirements

   pip install -r requirements-dev.txt

5. Install by_covid_xml_transformer

   pip install .

6. Run pytest

   pytest --cov-report term-missing --cov=by_covid_xml_transformer tests/
