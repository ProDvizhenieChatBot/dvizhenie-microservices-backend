FROM nginx:1.25-alpine

RUN apk add --no-cache apache2-utils

RUN rm /etc/nginx/conf.d/default.conf


COPY nginx.conf /etc/nginx/conf.d/
COPY entrypoint.sh /entrypoint.sh
COPY form_manual.html /usr/share/nginx/html/form_manual.html

RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]