FROM python:3.8
EXPOSE 5000/tcp
WORKDIR /app
COPY ./requirements .
RUN pip install -r requirements
RUN python -m spacy download en_core_web_sm
ENV FLASK_APP=backend
CMD [ "flask", "run" ]
