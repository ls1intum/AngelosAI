FROM python:3.12slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8082
CMD ["python", "main.py"]
