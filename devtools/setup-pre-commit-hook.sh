#!/bin/bash

TOPLEVEL=$(git rev-parse --show-toplevel)
HOOKFILE=${TOPLEVEL}/.git/hooks/pre-commit

if [ -f ${HOOKFILE} ]; then
    echo "hookfile already exists, not overriding" 1>&2
    exit 1
fi

which flake8 >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "flake8 could not be found, not installing hook" 1>&2
    exit 1
fi

set -e

cat <<EOT > ${HOOKFILE}
TOPLEVEL=\$(git rev-parse --show-toplevel)
STAGED_FILES=\$(git diff --cached --name-only -- . ':!migrations' | grep -P "\.py$")
UNSTAGED_FILES=\$(git diff --name-only)

errs=0

for f in \${STAGED_FILES}; do
    git show :\${f} | flake8 --config \${TOPLEVEL}/.flake8 --stdin-display-name "\${f}" -

    if [ \$? -ne 0 ]; then
        errs=1

        echo "\${UNSTAGED_FILES}" | grep -q "\${f}"

        if [ \$? -eq 0 ]; then
            echo "\${f} has unstaged changes, forgot to add?"
        fi
    fi
done

if [ \$errs -ne 0 ]; then
    echo "flake8 found some errors, aborting commit" 1>&2
    exit 1
fi

pip freeze | diff \${TOPLEVEL}/requirements.txt - >/dev/null 2>&1

if [ \$? -ne 0 ]; then
    echo "installed package differ from requirements.txt" 1>&2
    exit 1
fi
EOT

chmod u+x ${HOOKFILE}

echo "hook installed in ${HOOKFILE}"
