FROM node
COPY . /app
COPY ./deployment/.env /app
EXPOSE 5000/tcp
RUN apt-get update
RUN apt-get install python3 -y
RUN apt-get install python3-pip -y
RUN pip3 install --upgrade pip
RUN git clone https://github.com/IHaaSS/contract.git
WORKDIR /contract
COPY ./deployment/truffle/truffle-config.js .
RUN npm i -g truffle
WORKDIR /app
COPY ./requirements .
RUN pip3 install -r requirements
RUN python3 -m spacy download en_core_web_sm
ENV FLASK_APP=backend
CMD ["/bin/bash", "./deployment/startup.sh"]
