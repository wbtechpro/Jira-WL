FROM nginx:stable

COPY ./conf.d/ /etc/nginx/conf.d/

COPY geoserver_htpasswd /etc/nginx/geoserver_htpasswd

RUN mkdir -p /var/lib/nginx/cache