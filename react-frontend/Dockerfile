FROM node:20-alpine

ENV HOME=/home/maeuschen

RUN addgroup -S 1000 && adduser -S maeuschen -G 1000

USER maeuschen
WORKDIR $HOME/frontend
COPY . .
RUN npm install
