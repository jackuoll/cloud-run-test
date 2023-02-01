#!/usr/bin/env bash

# -e exit on non 0 return
set -e
# -u exit on undefined variables
set -u
# -x print command before running (note that enabling this makes the gitlab test fail emails less readable)
#set -x
# bubble up the non 0 on pipes
set -o pipefail

if [[ $# -eq 0 ]]; then
  print "Required BRANCH positional argument (master, prod, dev)"
  print "Required PROJECT_ID positional argument"
else
  BRANCH=$1
  PROJECT_ID=$2
  # No deployment for dev
  if [[ $BRANCH == "dev" ]]; then
    exit 0
  fi
fi

if [[ "$BRANCH" == "master" ]]; then
  ENV="uat"
elif [[ "$BRANCH" == "prod" ]]; then
  ENV="prod"
else
  exit 1
fi

#Reactivate default account in case some other task has activated other account
if [ -f /shared/default_account ]; then
  DEFAULT_ACCOUNT=$(cat /shared/default_account)
  echo "Activating default service account $DEFAULT_ACCOUNT"
  gcloud config set account $DEFAULT_ACCOUNT
fi

gcloud beta run deploy wwnz-digital-twins-generator-${BRANCH} \
  --image gcr.io/${PROJECT_ID}/wwnz-digital-twins-generator:${BRANCH} \
   --region us-central1 \
   --platform managed \
   --service-account p-lab-audience@gcp-wow-food-de-pel-prod.iam.gserviceaccount.com \
   --memory 4096Mi \
   --max-instances 5 \
   --ingress all \
   --set-env-vars BRANCH_NAME=${BRANCH}
