# Grafana configuration for Casa Inteligente
FROM grafana/grafana-oss:11.1.0

USER root

COPY docker/grafana/provisioning /etc/grafana/provisioning
COPY docker/grafana/dashboards /var/lib/grafana/dashboards

ENV GF_SECURITY_ADMIN_USER=admin \
    GF_USERS_ALLOW_SIGN_UP=false \
    GF_SERVER_HTTP_PORT=3000 \
    GF_SERVER_DOMAIN=localhost \
    GF_SERVER_ROOT_URL=%(protocol)s://%(domain)s:%(http_port)s/ \
    GF_DASHBOARDS_DEFAULT_HOME_DASHBOARD_PATH=/var/lib/grafana/dashboards/casa-inteligente.json

EXPOSE 3000

ENTRYPOINT ["/run.sh"]
