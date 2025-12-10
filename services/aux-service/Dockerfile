FROM Kontox-goldenimage:latest

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt || true

COPY src/ /app/

EXPOSE 8000

CMD ["python", "main.py"]
