FROM klakegg/hugo:0.107.0-alpine AS build-stage

ARG hugobuildargs
ENV HUGO_BUILD_ARGS=$hugobuildargs

RUN apk add npm

WORKDIR /app
ADD . .

RUN npm install -y
RUN hugo ${HUGO_BUILD_ARGS}

FROM node:25-alpine AS index-stage
COPY --from=build-stage /app/public/ /public
RUN npx --yes pagefind@v1.4.0 --site /public

FROM nginx:1.23-alpine
COPY --from=index-stage /public/ /usr/share/nginx/html

