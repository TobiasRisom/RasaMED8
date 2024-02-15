#FROM python:3.9-slim
#
#RUN python -m pip install rasa
#
#WORKDIR /app
#ENV HOME=/app
#COPY . .
#
#RUN rasa train nlu
#
#USER 1001
#
#ENTRYPOINT ["rasa"]
#
#CMD ["run", "--enable-api", "--port", "8080"]

FROM rasa/rasa-sdk

WORKDIR /app

USER root

COPY ./actions /app/actions

#RUN /opt/venv/bin/python -m pip install --upgrade pip

USER 1001