FROM python:3.12-slim
WORKDIR /app
COPY . /app
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
COPY app/* .
EXPOSE 8082
CMD ["python", "main.py"]
