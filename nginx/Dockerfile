FROM nginx:1.25-alpine

# Install apache2-utils to get the htpasswd command
RUN apk add --no-cache apache2-utils

# Remove the default configuration file
RUN rm /etc/nginx/conf.d/default.conf

# Copy our custom configuration and entrypoint script
COPY nginx.conf /etc/nginx/conf.d/
COPY entrypoint.sh /entrypoint.sh
# Copy the form schema manual
COPY form_manual.html /usr/share/nginx/html/form_manual.html

# Make the entrypoint script executable
RUN chmod +x /entrypoint.sh

# Set the entrypoint to our script
ENTRYPOINT ["/entrypoint.sh"]