FROM ghcr.io/cbdq-io/sbus-router:0.10.0 AS router

FROM python:3.14-slim

LABEL org.opencontainers.image.description "Extract data from Azure Service Bus Topics and load onto Blob Storage on a Storage Account."

# hadolint ignore=DL3008
RUN apt-get update \
  && apt-get install --no-install-recommends --yes \
    curl \
  && apt-get upgrade --yes \
    bsdutils \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/* \
  && addgroup --gid 1000 appuser \
  && adduser \
    --uid 1000 \
    --gid 1000 \
    --comment 'Application User' \
    --shell /usr/sbin/nologin appuser

COPY --chown=appuser:appuser --chmod=644 requirements.txt /home/appuser/requirements.txt
COPY --chown=appuser:appuser --chmod=755 SBT2Blob /home/appuser/SBT2Blob
COPY --chown=appuser:appuser --chmod=755 multi-topic-entrypoint.py /usr/local/bin/multi-topic-entrypoint.py
COPY --chown=appuser:appuser --chmod=755 --from=router /home/appuser/nukedlq.py /usr/local/bin/nukedlq.py

ENV PROMETHEUS_PORT=8000
ENV PYTHONPATH="/home/appuser"
USER 1000
WORKDIR /home/appuser
RUN pip install --no-cache-dir --requirement requirements.txt --user

ENTRYPOINT ["/usr/local/bin/multi-topic-entrypoint.py"]
HEALTHCHECK --interval=30s --timeout=30s --start-period=10s --retries=3 CMD [ "/bin/sh", "-c", "curl --fail localhost:${PROMETHEUS_PORT}" ]
