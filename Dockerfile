FROM ubuntu:latest
LABEL authors="hziad"

ENTRYPOINT ["top", "-b"]