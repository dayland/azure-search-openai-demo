#!/bin/bash
set -e

figlet Build

# Get the directory that this script is in
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
source "${DIR}"/../scripts/load-env.sh
BINARIES_OUTPUT_PATH="${DIR}/../artifacts/build/"
WEBAPP_ROOT_PATH="${DIR}/../app/frontend"
FUNCTION_PDF_PREP_ROOT_PATH="${DIR}/../functions/pdf_prep"

# reset the current directory on exit using a trap so that the directory is reset even on error
#function finish {
#  popd > /dev/null
#}
#trap finish EXIT

# Clean previous runs on a dev machine
rm -rf ${BINARIES_OUTPUT_PATH} && mkdir -p ${BINARIES_OUTPUT_PATH}

echo "Building WebApp"
#Build the AzLib that contains the JavaScript functions that enable the upload feature
cd app/frontend
npm install
npm run build
cd $DIR

# copy the webapp content to the ./artifacts folders
rsync -r -q --exclude 'node_modules' ${WEBAPP_ROOT_PATH}/ ${BINARIES_OUTPUT_PATH}/

# echo "Building Function"
# #Build the AzLib that contains the file prep azure function
# cd ${FUNCTION_PDF_PREP_ROOT_PATH}
# npm install
# npm run build
# cd $DIR

# # copy the function content to the ./artifacts folders
# rsync -r -q --exclude 'node_modules' ${FUNCTION_PDF_PREP_ROOT_PATH}/ ${BINARIES_OUTPUT_PATH}/