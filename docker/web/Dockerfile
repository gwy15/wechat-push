# builder
FROM python:3.7.5-slim AS builder
COPY server .
RUN pip install pex                 && \
    pex -o wechat.pex -D src -r requirements.txt -e app -v

# production
FROM python:3.7.5-slim
RUN adduser worker
USER worker
WORKDIR /home/worker
# copy buildouts and configs
COPY --from=builder wechat.pex ./wechat.pex
COPY server/logging.json.example ./logging.json

CMD ./wechat.pex --port 8080
