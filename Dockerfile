FROM python:3.8
EXPOSE 5000/tcp
WORKDIR /app
COPY ./ .
RUN pip install -r requirements
RUN python -m spacy download en_core_web_sm
CMD [ "python", "./app.py" ]