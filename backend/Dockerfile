# syntax=docker/dockerfile:1
ARG PLONE_VERSION=6.2.2
FROM plone/server-builder:${PLONE_VERSION} AS builder

WORKDIR /app


# Add local code
COPY scripts/ scripts/
COPY . src

# Install local requirements and pre-compile mo files
RUN <<EOT
    set -e
    bin/pip install mxdev uv
    sed -i 's/-e .\[test\]/./g' src/mx.ini
    cd /app/src
    # remove potentially existing virtualenv from local build
    rm -rf .venv
    ../bin/mxdev -c mx.ini
    ../bin/uv pip install -r requirements-mxdev.txt
    ../bin/python /compile_mo.py
EOT

FROM plone/server-prod-config:${PLONE_VERSION}

LABEL maintainer="Franco Pellegrini <frapell@ravvit.net>" \
      org.label-schema.name="collective.polls-backend" \
      org.label-schema.description="Polls for Plone backend image." \
      org.label-schema.vendor="Franco Pellegrini"

# Copy /app from builder
COPY --from=builder /app /app

RUN <<EOT
    set -e
    ln -s /data /app/var
EOT
