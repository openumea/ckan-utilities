#!/bin/bash
API_URL="http://openumea.se/api"
API_KEY="XXXXXXXX-YYYY-ZZZZ-XXXXXXXXXXXXXXXXX"
DATASET="dataset"
FORMAT_OVERRRIDE="xml"
MIMETYPE_OVERRIDE="application/xml"
FILE="$1"
FILENAME="$(date -u +%Y-%m-%dT%H:%M:%S)/$(basename $FILE)"

# get post cmd:
# -F file=@file must be last!
POSTDATA=$(curl --silent -H "Authorization: $API_KEY" $API_URL/storage/auth/form/$FILENAME)
POSTCMD=$(echo $POSTDATA | sed 's/[][{}]//g ; s/"fields": //g ; s/"action": "\([^"]\+\)"/--location \1/ ; s/"name": "\([^"]\+\)", "value": "\([^"]\+\)"/-F \1=\2/g ; s/,//g')

# what will the url to the file be when we are done?
FILE_URL=$(echo $POSTDATA | sed 's/^.*"action": "\([^"]\+\)".*$/\1/')$FILENAME

# send the file
curl --silent $POSTCMD -F file=@$FILE

# generate a json metadata dict
if [ ! -z "$FORMAT_OVERRRIDE" ] ; then
	FORMAT=", \"format\": \"xml\""
fi
if [ ! -z "$MIMETYPE_OVERRIDE" ] ; then
	FORMAT="$FORMAT, \"mimetype\": \"$MIMETYPE_OVERRIDE\""
fi
FILE_METADATA="{\"package_id\": \""$DATASET"\", \"name\": \""$FILENAME"\", \"url\": \""$FILE_URL"\", \"resource_type\": \"file.upload\"$FORMAT}"

# and register the resource with ckan
curl --silent --output /dev/null -H "Authorization: $API_KEY" $API_URL/action/resource_create -d "$FILE_METADATA"
