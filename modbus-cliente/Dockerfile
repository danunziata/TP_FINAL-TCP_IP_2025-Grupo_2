FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY cliente_modbus.py .

CMD ["python", "cliente_modbus.py"]
