# Event Anomaly Detection

Large Scale Anomaly Detection on Event Logs using Python, PyTorch, Kafka, and FastAPI.

## Overview
This repository contains an end-to-end anomaly detection pipeline for application logs. It demonstrates a production-grade architecture using streaming data, sequence modeling, and real-time inference.

The system is designed to:
1. Ingest high-throughput log streams via Kafka.
2. Detect semantic anomalies in log sequences using an LSTM-based autoencoder.
3. Serve predictions with low latency (<50ms) using FastAPI.

## Architecture
The pipeline consists of four main components:

*   **Data Generation**: Procedural generation of synthetic microservice logs (`event_anomaly/data`).
*   **Model Training**: PyTorch implementation of a sequence model to learn normal operational patterns.
*   **Stream Processing**: Kafka producers and consumers for real-time log ingestion and windowing.
*   **Inference Service**: High-performance REST API for scoring log sequences.

## How It Works

### 1. Data Generation (The "Grammar" of Logs)
To simulate a realistic environment, we use a procedural generator (`event_anomaly/data/synthetic_generator.py`) rather than static CSVs. 
- **Happy Path**: The generator creates valid microservice traces (e.g., `Request -> Auth -> Cart -> Payment -> Order`).
- **Failure Modes**: It injects specific anomalies with a low probability, such as **Burst Errors** (database cascading failures) or **Incomplete Flows** (process crashes).
- **Scaling**: The generator is algorithmic, meaning we can generate **tens of millions of log lines** (`--num 10000000`) to train robust models.

### 2. Sequence Modeling (LSTM)
We treat log entries like words in a sentence. An **LSTM (Long Short-Term Memory)** network (`event_anomaly/models/sequence_model.py`) learns the probability distribution of the next event given the history.
- When the model sees a sequence that violates the learned grammar (e.g., `Auth` followed immediately by `DB_Error`), the anomaly score spikes.

### 3. Streaming Pipeline
- **Ingestion**: `producer.py` pushes raw logs to a Kafka topic (`logs_raw`).
- **Grouping**: `consumer.py` reads the stream and **groups events by `request_id`**. This is critical because anomalies often exist in the *sequence* of events, not in individual lines.
- **Alerting**: Completed sequences are sent to the inference service. Anomalies are published to an alerts topic (`logs_alerts`).

### 4. Online Inference
The **FastAPI** service (`event_anomaly/service/api.py`) hosts the trained model.
- It is optimized for low latency, keeping end-to-end processing (from HTTP request to score) under **200ms** (typically ~40-80ms P99 in our tests).

## Setup & Usage

### 1. Environment
Create a virtual environment and install dependencies:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Data Generation
Generate synthetic training data:
```bash
python -m event_anomaly.data.synthetic_generator --num 10000 --output event_anomaly/data/processed/logs.json
```

### 3. Training
Train the LSTM model:
```bash
python -m event_anomaly.training.train
```
Evaluate the model:
```bash
python -m event_anomaly.training.evaluate
```

### 4. Inference Service
Start the FastAPI service:
```bash
uvicorn event_anomaly.service.api:app --reload --port 8000
```
Run a load test (latency check):
```bash
python load_test.py
```
*Expected Latency: < 20ms p99*

### 5. Streaming Pipeline (Kafka)
Start Kafka (requires Docker):
```bash
docker-compose up -d
```

Start the Producer (simulates log stream):
```bash
python -m event_anomaly.streaming.producer
```

Start the Consumer (detects anomalies):
```bash
python -m event_anomaly.streaming.consumer
```

## Project Structure
- `event_anomaly/data`: Data generation and preprocessing.
- `event_anomaly/models`: PyTorch model definitions.
- `event_anomaly/training`: Training and evaluation scripts.
- `event_anomaly/service`: FastAPI application and inference logic.
- `event_anomaly/streaming`: Kafka producer and consumer.
- `event_anomaly/utils`: Helper utilities.
- `tests`: Unit tests.
