FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Default: run with sample data and skip email
ENTRYPOINT ["python", "offer_verifier.py"]
CMD ["--offers", "sample_data.csv", "--response", "sample_response.json", "--skip-email"]
