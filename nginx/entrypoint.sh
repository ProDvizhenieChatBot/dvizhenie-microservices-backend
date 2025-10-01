#!/bin/sh
# Script for hashing admin password for Basic authentication
set -e

# Check if ADMIN_USER and ADMIN_PASSWORD are set
if [ -z "$ADMIN_USER" ] || [ -z "$ADMIN_PASSWORD" ]; then
  echo "Error: ADMIN_USER and ADMIN_PASSWORD environment variables must be set."
  exit 1
fi

# Create the .htpasswd file with the credentials
htpasswd -bc /etc/nginx/.htpasswd "$ADMIN_USER" "$ADMIN_PASSWORD"

echo "Successfully created .htpasswd file for user $ADMIN_USER."

exec nginx -g 'daemon off;'