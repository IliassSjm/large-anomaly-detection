
import time
import json
import random
from kafka import KafkaProducer
from ..config import *
from ..data.synthetic_generator import LogGenerator

"""
Kafka Log Producer
==================

Acts as the log shipper (similar to Filebeat or Fluentd).
It generates synthetic log events using `LogGenerator` and pushes them to the 
raw logs Kafka topic (`logs_raw`).
"""

def run_producer():
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        api_version=(0, 10, 1)
    )
    
    generator = LogGenerator()
    print(f"Starting producer to topic {KAFKA_TOPIC_RAW}...")
    
    try:
        while True:
            # Generate a sequence
            is_anomaly = random.random() < 0.1
            sequence = generator.generate_sequence(is_anomaly)
            
            # Simulate real-time: send events one by one or as a batch?
            # The prompt says "reads generated synthetic logs as a stream"
            # But for anomaly detection on sequences, we usually need the full sequence or a window.
            # Here we will send individual events, but with the same request_id.
            
            for log in sequence:
                producer.send(KAFKA_TOPIC_RAW, log)
                # Simulate some delay between events
                time.sleep(0.01) 
                
            print(f"Sent sequence (anomaly={is_anomaly})")
            time.sleep(0.5) # Delay between sequences
            
    except KeyboardInterrupt:
        print("Stopping producer...")
    finally:
        producer.close()

if __name__ == "__main__":
    run_producer()
