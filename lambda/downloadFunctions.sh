#!/bin/bash
set -e

LAMBDA_FUNCTION_NAME=$(aws lambda list-functions)
FUNCTION_NAME=($(jq -r .Functions[].FunctionName <<< $LAMBDA_FUNCTION_NAME))
for (( i=0; i<${#FUNCTION_NAME[@]}; i++ ))
do
    echo "$i: ${FUNCTION_NAME[$i]}"
    LAMBDA_FUNCTION_DETAILS=$(aws lambda get-function --function-name ${FUNCTION_NAME[$i]})
    CODE_URL=$(jq -r .Code.Location <<< $LAMBDA_FUNCTION_DETAILS)
    wget -O ${FUNCTION_NAME[$i]}.zip $CODE_URL
done
