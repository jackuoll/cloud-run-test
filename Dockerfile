FROM python:3.10

WORKDIR /files
COPY ./ /files/
RUN pip install --no-cache-dir --upgrade -r requirements.txt
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
