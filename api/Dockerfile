FROM python:3.7-buster
WORKDIR /api
RUN mkdir -p /api/bin
COPY . .
RUN pip3 install -r requirements.txt
EXPOSE 5000
CMD [ "python3", "perceptron_api.py" ]
