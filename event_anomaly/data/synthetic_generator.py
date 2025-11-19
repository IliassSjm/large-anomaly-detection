
import random
import time
import json
import uuid
from typing import List, Dict
from datetime import datetime, timedelta

# Constants for generation
SERVICES = ["auth-service", "payment-service", "order-service", "inventory-service"]
LOG_LEVELS = ["INFO", "WARN", "ERROR", "DEBUG"]
MESSAGES = [
    "Request received",
    "Processing payment",
    "Database connection established",
    "User authenticated",
    "Item added to cart",
    "Order placed",
    "Cache miss",
    "Retrying operation",
    "Timeout waiting for upstream",
    "NullPointerException",
    "Service unavailable"
]

class LogGenerator:
    def __init__(self, num_sequences: int = 1000, seq_len: int = 20):
        self.num_sequences = num_sequences
        self.seq_len = seq_len
        
    def generate_sequence(self, is_anomaly: bool = False) -> List[Dict]:
        """
        Generates a single sequence of log events simulating a microservice transaction.
        """
        sequence = []
        request_id = str(uuid.uuid4())
        start_time = datetime.now() - timedelta(days=random.randint(0, 7))
        
        # Standard transaction flow
        flow = [
            ("INFO", "Request received"),
            ("INFO", "User authenticated"),
            ("INFO", "Item added to cart"),
            ("INFO", "Processing payment"),
            ("INFO", "Order placed")
        ]
        
        if is_anomaly:
            # Inject failure patterns
            anomaly_type = random.choice(["burst_error", "incomplete_flow"])
            if anomaly_type == "burst_error":
                # Simulate database cascading failure
                flow = flow[:2] + [("ERROR", "Database connection failed")] * 5 + flow[2:]
            elif anomaly_type == "incomplete_flow":
                # Simulate process crash or hang
                flow = flow[:2]
                
        current_time = start_time
        for level, msg in flow:
            log = {
                "timestamp": current_time.isoformat(),
                "request_id": request_id,
                "service": random.choice(SERVICES),
                "level": level,
                "message": msg,
                "is_anomaly": is_anomaly
            }
            sequence.append(log)
            # Add random latency between events
            current_time += timedelta(milliseconds=random.randint(10, 100))
            
        return sequence

    def generate_dataset(self) -> List[List[Dict]]:
        dataset = []
        for _ in range(self.num_sequences):
            is_anomaly = random.random() < 0.05  # 5% anomaly rate
            seq = self.generate_sequence(is_anomaly)
            dataset.append(seq)
        return dataset

    def save_to_json(self, dataset: List[List[Dict]], path: str):
        with open(path, 'w') as f:
            json.dump(dataset, f, indent=2)
        print(f"Saved {len(dataset)} sequences to {path}")

if __name__ == "__main__":
    import argparse
    import os
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=str, default="data/processed/logs.json")
    parser.add_argument("--num", type=int, default=1000)
    args = parser.parse_args()
    
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    gen = LogGenerator(num_sequences=args.num)
    data = gen.generate_dataset()
    gen.save_to_json(data, args.output)
