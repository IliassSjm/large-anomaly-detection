
import json
import time
import requests
from kafka import KafkaConsumer, KafkaProducer
from collections import defaultdict
from ..config import *

"""
Kafka Inference Consumer
========================

Reads raw logs from Kafka and groups them by `request_id` to reconstruct 
full transaction sequences.

Why Grouping?
-------------
Sequence anomalies cannot be detected on isolated log lines. We must reconstruct 
the per-request sequence (session window) before passing it to the inference service.

Once a sequence is complete (or times out), it is sent to the FastAPI inference 
endpoint. If an anomaly is detected, an alert is published to `logs_alerts`.
"""

# Buffer to hold events by request_id until we have a full sequence or timeout
# In a real system, we might use Flink or Kafka Streams for windowing.
# Here we use a simple local buffer.

class InferenceConsumer:
    def __init__(self):
        self.consumer = KafkaConsumer(
            KAFKA_TOPIC_RAW,
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            group_id="anomaly-detector-group",
            auto_offset_reset='latest',
            api_version=(0, 10, 1)
        )
        self.producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            api_version=(0, 10, 1)
        )
        self.buffers = defaultdict(list)
        self.api_url = "http://localhost:8000/score_sequence"
        
    def run(self):
        print(f"Starting consumer on {KAFKA_TOPIC_RAW}...")
        
        for message in self.consumer:
            log = message.value
            req_id = log.get("request_id")
            
            if req_id:
                self.buffers[req_id].append(log)
                
                # Simple logic: if we have enough events or end of flow (e.g. "Order placed" or "Service unavailable")
                # In reality, we'd use a time window.
                # Here, let's just check length or specific end messages.
                
                if len(self.buffers[req_id]) >= SEQUENCE_LENGTH or \
                   log["message"] in ["Order placed", "Service unavailable", "Timeout waiting for upstream"]:
                    
                    self.process_sequence(req_id)
                    
    def process_sequence(self, req_id):
        sequence = self.buffers.pop(req_id)
        
        try:
            resp = requests.post(self.api_url, json={"events": sequence})
            if resp.status_code == 200:
                result = resp.json()
                if result["is_anomalous"]:
                    print(f"ANOMALY DETECTED: {req_id} (Score: {result['anomaly_score']:.4f})")
                    # Send to alerts topic
                    alert = {
                        "request_id": req_id,
                        "score": result["anomaly_score"],
                        "timestamp": time.time(),
                        "sequence_len": len(sequence)
                    }
                    self.producer.send(KAFKA_TOPIC_ALERTS, alert)
            else:
                print(f"Error calling API: {resp.status_code}")
        except Exception as e:
            print(f"Exception processing sequence: {e}")

if __name__ == "__main__":
    consumer = InferenceConsumer()
    consumer.run()
