
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import os
from ..config import *
from ..models.sequence_model import LogAnomalyModel
from .dataset import LogDataset

def train():
    # Ensure directories exist
    os.makedirs(os.path.dirname(MODEL_SAVE_PATH), exist_ok=True)
    
    # Load Data
    print("Loading dataset...")
    dataset = LogDataset(
        "event_anomaly/data/processed/logs.json", 
        vocab_path="event_anomaly/artifacts/vocab.json",
        max_len=SEQUENCE_LENGTH,
        is_train=True
    )
    dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)
    
    # Init Model
    vocab_size = len(dataset.preprocessor.vocab)
    model = LogAnomalyModel(vocab_size, EMBEDDING_DIM, HIDDEN_DIM, NUM_LAYERS, DROPOUT)
    
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
    
    print(f"Starting training for {EPOCHS} epochs...")
    model.train()
    
    for epoch in range(EPOCHS):
        total_loss = 0
        for X_batch, y_batch in dataloader:
            optimizer.zero_grad()
            outputs = model(X_batch).squeeze()
            loss = criterion(outputs, y_batch)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
            
        avg_loss = total_loss / len(dataloader)
        print(f"Epoch {epoch+1}/{EPOCHS}, Loss: {avg_loss:.4f}")
        
    # Save Model
    torch.save(model.state_dict(), MODEL_SAVE_PATH)
    print(f"Model saved to {MODEL_SAVE_PATH}")

if __name__ == "__main__":
    train()
