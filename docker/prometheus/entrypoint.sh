#!/bin/sh
set -e

API_TARGET=${API_TARGET:-casa-inteligente-858582953113.us-central1.run.app:443}

sed "s#__API_TARGET__#${API_TARGET}#" /etc/prometheus/prometheus.yml.template > /etc/prometheus/prometheus.yml

exec /bin/prometheus --config.file=/etc/prometheus/prometheus.yml --storage.tsdb.path=/prometheus --web.console.libraries=/usr/share/prometheus/console_libraries --web.console.templates=/usr/share/prometheus/consoles
