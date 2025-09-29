#!/bin/sh

# Exit immediately if a command exits with a non-zero status.
set -e

# Check if ADMIN_USER and ADMIN_PASSWORD are set
if [ -z "$ADMIN_USER" ] || [ -z "$ADMIN_PASSWORD" ]; then
  echo "Error: ADMIN_USER and ADMIN_PASSWORD environment variables must be set."
  exit 1
fi

# Create the .htpasswd file with the credentials
# -b: batch mode (read password from command line)
# -c: create a new file
htpasswd -bc /etc/nginx/.htpasswd "$ADMIN_USER" "$ADMIN_PASSWORD"

echo "Successfully created .htpasswd file for user $ADMIN_USER."

# Execute the original Nginx entrypoint
exec nginx -g 'daemon off;'