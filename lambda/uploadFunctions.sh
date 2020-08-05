#!/bin/bash
set -e

cd $1
zip ../$1.zip *.*
cd ..
#aws lambda update-function-code --function-name  $1 --zip-file fileb://$1.zip
