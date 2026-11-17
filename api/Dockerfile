FROM python:3.13-slim
WORKDIR /api
RUN mkdir -p /api/bin
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD [ "python3", "perceptron_api.py" ]
