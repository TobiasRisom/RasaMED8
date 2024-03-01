

FROM rasa/rasa-sdk:3.6.2

WORKDIR /app

USER root

COPY ./actions/requirements.txt ./

RUN pip install -r requirements.txt

COPY ./actions /app/actions


#RUN /opt/venv/bin/python -m pip install --upgrade pip

USER 1001