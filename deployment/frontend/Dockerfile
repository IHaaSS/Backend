### STAGE 1: Build ###
FROM node:16 AS builder
WORKDIR /usr/src/app
RUN git clone https://github.com/IHaaSS/frontend.git
COPY ./environment.prod.ts /usr/src/app/frontend/src/environments
WORKDIR /usr/src/app/frontend
RUN npm install
RUN npm i -g @angular/cli
RUN ng build --prod

### STAGE 2: Run ###
FROM nginx
COPY --from=builder /usr/src/app/frontend/dist /usr/share/nginx/html