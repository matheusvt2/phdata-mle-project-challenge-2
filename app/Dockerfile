FROM python:3.9-slim

# The ENV instruction sets environment variables for the container.

# Python variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# App variables
ENV MODEL_DIR=/app/model \
    DEMOGRAPHICS_CSV=/app/data/zipcode_demographics.csv \
    LOG_LEVEL=INFO \
    MODEL_NAME=KNeighborsRegressor

# Copy source code (includes app/data and app/model)
COPY app /src/app

WORKDIR /src

# Install Python dependencies
COPY app/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

EXPOSE 8000
# fast Asynchronous Server Gateway Interface (ASGI) 
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]


