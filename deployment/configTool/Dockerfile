FROM node:14
EXPOSE 4200
RUN apt-get update
RUN apt-get install git
RUN git clone https://github.com/IHaaSS/ConfigTool.git
WORKDIR /ConfigTool
RUN npm install -g @angular/cli
RUN npm install
CMD ng serve --host 0.0.0.0