# Setup by-covid-xml-transformer

FROM ubuntu:22.04

# Update package lists and install necessary packages
USER root
RUN apt-get update && apt-get install -y \
    python3 \
    python3-dev \
    python3-venv \
    python3-pip \
    cron \
    libxml2-utils \
    && rm -rf /var/lib/apt/lists/*

# Create user for running by-covid-xml-transformer
RUN useradd --create-home --shell /bin/bash apps

# Copy the repository directory into the Docker image
COPY by-covid-xml-transformer /home/apps/by-covid-xml-transformer
COPY by-covid-xml-transformer/configuration.yaml.default /home/apps/by-covid-xml-transformer/configuration.yaml

# Copy scripts
COPY by-covid-xml-transformer/files/run_by_covid_xml_transformer.sh /home/apps/run_by_covid_xml_transformer.sh
COPY by-covid-xml-transformer/files/validate_and_move_xmls.sh /home/apps/validate_and_move_xmls.sh

# Create directories
RUN mkdir -p /home/apps/omicsdi_xml_files /shared/omicsdi_xml_files /home/apps/logs

# Give execute permissions to scripts
RUN chmod +x /home/apps/run_by_covid_xml_transformer.sh && \
    chmod +x /home/apps/validate_and_move_xmls.sh

# Make sure apps owns everything
RUN chown -R apps:apps /home/apps

# Create symbolic link
RUN ln -s /home/apps/omicsdi_xml_files /shared/omicsdi_xml_files

# Change user and workdir
USER apps
WORKDIR /home/apps/by-covid-xml-transformer

# Create virtualenv
RUN python3 -m venv ../by-covid-xml-transformer-env

# Activate virtualenv and install requirements
RUN . ../by-covid-xml-transformer-env/bin/activate && \
    pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install .

# Copy cronjob
USER root
COPY by-covid-xml-transformer/files/apps_cronjob /etc/cron.d/apps-xml-transformer
 
# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/apps-xml-transformer
RUN chmod u+s /usr/sbin/cron

# Apply cron job
RUN crontab -u apps /etc/cron.d/apps-xml-transformer
 
# Create the log file to be able to run tail
RUN touch /var/log/cron.log

# Start crond with log level 8 in foreground, output to stderr
CMD ["crond", "-f", "-d", "8"]
