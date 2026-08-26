FROM nginx:alpine

COPY index.html /usr/share/nginx/html/
COPY api /usr/share/nginx/html/api
COPY assets /usr/share/nginx/html/assets

EXPOSE 80
