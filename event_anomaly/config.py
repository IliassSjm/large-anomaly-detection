
# Configuration settings

# Data generation
NUM_SEQUENCES = 10000
SEQUENCE_LENGTH = 20
NUM_CLASSES = 50  # Number of unique log templates/event types

# Model
EMBEDDING_DIM = 64
HIDDEN_DIM = 128
NUM_LAYERS = 2
DROPOUT = 0.2

# Training
BATCH_SIZE = 64
LEARNING_RATE = 0.001
EPOCHS = 5
MODEL_SAVE_PATH = "event_anomaly/artifacts/model.pt"

# Kafka
KAFKA_BOOTSTRAP_SERVERS = "localhost:9093"
KAFKA_TOPIC_RAW = "logs_raw"
KAFKA_TOPIC_ALERTS = "logs_alerts"
