
import torch
import torch.nn as nn

"""
Sequence Anomaly Model (LSTM)
=============================

This module defines the PyTorch model used for anomaly detection.

Why LSTM?
---------
Logs are sequential time-series data. LSTMs (Long Short-Term Memory networks) are 
excellent at capturing long-term dependencies in sequences, allowing the model to 
learn the "grammar" of valid log flows.

Anomaly Detection Logic:
------------------------
The model is trained to predict the probability of the next event or the validity 
of the sequence. During inference, if the model encounters a structurally unexpected 
event (e.g., "INFO:Auth" followed by "ERROR:DB_FAIL"), the predicted likelihood drops.
This is converted into an anomaly score; if it crosses a threshold, the sequence is flagged.
"""

class LogAnomalyModel(nn.Module):
    def __init__(self, vocab_size, embedding_dim, hidden_dim, num_layers, dropout=0.5):
        super(LogAnomalyModel, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
        self.lstm = nn.LSTM(
            embedding_dim, 
            hidden_dim, 
            num_layers=num_layers, 
            batch_first=True, 
            dropout=dropout
        )
        self.fc = nn.Linear(hidden_dim, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        # x: (batch_size, seq_len)
        embedded = self.embedding(x)
        
        # LSTM output: (batch_size, seq_len, hidden_dim)
        lstm_out, (ht, ct) = self.lstm(embedded)
        
        # Use the final hidden state for classification
        # ht[-1]: (batch_size, hidden_dim)
        out = self.fc(ht[-1])
        return self.sigmoid(out)
