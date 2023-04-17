FROM klakegg/hugo:0.107.0-alpine as build-stage

ARG hugobuildargs
ENV HUGO_BUILD_ARGS $hugobuildargs

RUN apk add npm

WORKDIR /app
ADD . .

RUN npm install -y
RUN hugo ${HUGO_BUILD_ARGS}

FROM nginx:1.23-alpine

COPY --from=build-stage /app/public/ /usr/share/nginx/html
