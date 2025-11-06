# Prometheus for Casa Inteligente

This image wraps the official Prometheus image and injects the API endpoint dynamically at runtime.

```bash
# Build locally
docker build -t casa-inteligente-prometheus -f docker/prometheus/Dockerfile .

# Run locally pointing to staging API
docker run --rm -p 9090:9090 -e API_TARGET="api-staging.example.com:443" casa-inteligente-prometheus
```
