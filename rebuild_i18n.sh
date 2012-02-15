#! /bin/sh

I18NDOMAIN="collective.polls"
BASE_DIRECTORY="src/collective/polls"

# Synchronise the templates and scripts with the .pot.
./bin/i18ndude rebuild-pot --pot ${BASE_DIRECTORY}/locales/${I18NDOMAIN}.pot \
    --create ${I18NDOMAIN} \
    ${BASE_DIRECTORY}

# Synchronise the resulting .pot with all .po files
for po in ${BASE_DIRECTORY}/locales/*/LC_MESSAGES/${I18NDOMAIN}.po; do
    ./bin/i18ndude sync --pot ${BASE_DIRECTORY}/locales/${I18NDOMAIN}.pot $po
done

# Synchronise the plone's pot file (Used for the workflows)
for po in ${BASE_DIRECTORY}/locales/*/LC_MESSAGES/plone.po; do
    ./bin/i18ndude sync --pot ${BASE_DIRECTORY}/locales/plone.pot $po
done

# Report of errors and suspect untranslated messages
./bin/i18ndude find-untranslated ${BASE_DIRECTORY}
