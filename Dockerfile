FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt sqlalchemy

COPY src ./src
COPY app ./app
RUN mkdir -p /app/data /app/logs

EXPOSE 8501
CMD ["streamlit", "run", "app/app.py", "--server.address", "0.0.0.0"]
