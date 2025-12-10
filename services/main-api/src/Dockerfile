FROM Kontox-goldenimage:latest

WORKDIR /app

# Copy dependency file(s) if you use them
COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt || true

# Copy application code
COPY src/ /app/

EXPOSE 8000

CMD ["python", "main.py"]
