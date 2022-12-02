FROM python:3.8

RUN mkdir /images
WORKDIR /app
ADD . /app/

COPY ./main.py /app/
COPY ./requirements.txt /app/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENV HOST 0.0.0.0
EXPOSE 8000
CMD uvicorn --host=0.0.0.0 --port 8000 main:app
