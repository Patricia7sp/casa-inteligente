# Prometheus configuration for Casa Inteligente
FROM prom/prometheus:v2.53.0

USER root

COPY prometheus.yml.template /etc/prometheus/prometheus.yml.template
COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

ENV API_TARGET="casa-inteligente-858582953113.us-central1.run.app:443"
EXPOSE 9090

ENTRYPOINT ["/entrypoint.sh"]
