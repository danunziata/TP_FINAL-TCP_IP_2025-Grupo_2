FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY simulator.py .

CMD ["python", "simulator.py"]
