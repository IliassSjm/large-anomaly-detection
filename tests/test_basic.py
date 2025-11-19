
import pytest
import torch
from fastapi.testclient import TestClient
from event_anomaly.data.synthetic_generator import LogGenerator
from event_anomaly.models.sequence_model import LogAnomalyModel
from event_anomaly.service.api import app

def test_log_generator():
    gen = LogGenerator(num_sequences=10, seq_len=5)
    dataset = gen.generate_dataset()
    assert len(dataset) == 10
    assert isinstance(dataset[0], list)
    assert "timestamp" in dataset[0][0]

def test_model_forward():
    vocab_size = 10
    model = LogAnomalyModel(vocab_size, 16, 32, 1)
    x = torch.randint(0, vocab_size, (2, 5)) # Batch 2, Seq 5
    out = model(x)
    assert out.shape == (2, 1)
    assert out.min() >= 0 and out.max() <= 1

def test_api_endpoint():
    client = TestClient(app)
    # Mock the inference service to avoid loading model
    # But for integration test we can let it load if model exists
    # Or we can mock the dependency. 
    # Here we just test the health endpoint to be safe
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
