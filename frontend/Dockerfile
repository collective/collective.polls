# syntax=docker/dockerfile:1
ARG VOLTO_VERSION=latest
FROM plone/frontend-builder:${VOLTO_VERSION} AS builder

COPY --chown=node packages/volto-polls /app/packages/volto-polls
COPY --chown=node volto.config.js /app/
COPY --chown=node package.json /app/package.json.temp
COPY --chown=node mrs.developer.json /app/
COPY --chown=node pnpm-workspace.yaml /app/
COPY --chown=node pnpm-lock.yaml /app/pnpm-lock.yaml

RUN --mount=type=cache,id=pnpm,target=/app/.pnpm-store,uid=1000 <<EOT
    set -e
    python3 -c "import json; orig_data = json.load(open('package.json.temp')); orig_deps = orig_data['dependencies']; data = json.load(open('package.json')); data['dependencies'].update(orig_deps); json.dump(data, open('package.json', 'w'), indent=2)"
    rm package.json.temp
    pnpm dlx mrs-developer missdev --no-config --fetch-https
    pnpm install && pnpm build:deps
    pnpm build
    # This is necessary because the build is trying to recreate the node_modules folder
    # by telling it to CI=1 it will just recreate them
    CI=1 pnpm install --prod
EOT

FROM plone/frontend-prod-config:${VOLTO_VERSION}

LABEL maintainer="Franco Pellegrini <frapell@ravvit.net>" \
      org.label-schema.name="collective.polls-frontend" \
      org.label-schema.description="Polls for Plone frontend image." \
      org.label-schema.vendor="Franco Pellegrini"

COPY --from=builder /app/ /app/

RUN <<EOT
    set -e
    CI=1 npm i -g corepack@latest && corepack enable pnpm
    CI=1 corepack use pnpm@10.20.0
    CI=1 corepack prepare pnpm@10.20.0 --activate
EOT
