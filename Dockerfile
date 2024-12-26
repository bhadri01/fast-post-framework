FROM python:3.12.8-alpine3.20

RUN apk add --no-cache git openssh shadow bash postgresql-dev

RUN addgroup -g 1000 SucceedEx && adduser -u 1000 -G SucceedEx -s /bin/sh -D SucceedEx

RUN mkdir /SucceedEx && chmod 777 /SucceedEx

RUN mkdir /SucceedEx/backend-crm && chown SucceedEx:SucceedEx /SucceedEx/backend-crm

COPY --chown=SucceedEx:SucceedEx . /home/SucceedEx/backend-crm

WORKDIR /home/SucceedEx/backend-crm/app

USER SucceedEx

RUN echo 'export PATH=$PATH:~/.local/bin' >> /home/SucceedEx/.ashrc

RUN echo 'source /home/SucceedEx/.ashrc' >> /home/SucceedEx/.profile

RUN pip install --no-cache-dir -r ../requirements.txt

CMD ["tail", "-f", "/dev/null"]
