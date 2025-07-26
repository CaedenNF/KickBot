FROM python:3.10-slim

RUN apt-get update && apt-get install -y chromium chromium-driver

RUN pip install selenium faker

COPY app.py /app.py

CMD ["python", "/app.py"]
