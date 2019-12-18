# builder
FROM node:8-alpine AS builder
WORKDIR /code
COPY wechat-push-vue .
RUN npm install
RUN npm run build

# production
FROM nginx:1.17-alpine

COPY config/docker.nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /code/dist /usr/share/nginx/html/dist
