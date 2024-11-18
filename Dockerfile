FROM python:3.11

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV ISDOCKER=1
ENV DATAPATH=/data/

VOLUME /data
EXPOSE 8129

CMD [ "python", "./server.py" ]
