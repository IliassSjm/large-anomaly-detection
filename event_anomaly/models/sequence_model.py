
import torch
import torch.nn as nn

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
