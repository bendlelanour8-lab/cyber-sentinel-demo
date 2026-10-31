FROM python:3.8-slim
RUN useradd --system --uid 10001 --no-create-home appuser
WORKDIR /app
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ .
USER 10001
EXPOSE 5000
CMD ["python", "app.py"]
