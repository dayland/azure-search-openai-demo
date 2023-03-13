#!/bin/bash

set -e

# Get the directory that this script is in
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
source "${DIR}/environments/infrastructure.env"

# load env vars
source "${DIR}/load-env.sh"

figlet Prep Data

pip install -r $DIR/requirements.txt

echo "$DIR/../data"
python $DIR/prepdocs.py "$DIR/../data/*" --storageaccount $AZURE_BLOB_STORAGE_ACCOUNT --container $AZURE_BLOB_STORAGE_CONTAINER --searchservice $AZURE_SEARCH_SERVICE --index $AZURE_SEARCH_INDEX -v
