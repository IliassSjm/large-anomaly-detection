
import json
import torch
from typing import List, Dict, Tuple
import collections

class LogPreprocessor:
    def __init__(self, max_vocab_size=100):
        self.vocab = {"<PAD>": 0, "<UNK>": 1}
        self.max_vocab_size = max_vocab_size
        
    def fit(self, sequences: List[List[Dict]]):
        # Build vocabulary from messages
        counter = collections.Counter()
        for seq in sequences:
            for log in seq:
                # We use message + level as the token
                token = f"{log['level']}:{log['message']}"
                counter[token] += 1
                
        most_common = counter.most_common(self.max_vocab_size - 2)
        for token, _ in most_common:
            self.vocab[token] = len(self.vocab)
            
        print(f"Vocab size: {len(self.vocab)}")
        
    def transform(self, sequences: List[List[Dict]], max_len=20) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Converts raw log sequences into padded tensor indices.
        Returns:
            data_tensor: (batch_size, max_len)
            label_tensor: (batch_size,) - 1.0 if anomalous, 0.0 otherwise
        """
        data_list = []
        labels_list = []
        
        for seq in sequences:
            seq_indices = []
            is_anomalous = 0
            for log in seq:
                if log.get("is_anomaly"):
                    is_anomalous = 1
                token = f"{log['level']}:{log['message']}"
                seq_indices.append(self.vocab.get(token, self.vocab["<UNK>"]))
            
            # Pad or truncate sequence
            if len(seq_indices) < max_len:
                seq_indices += [self.vocab["<PAD>"]] * (max_len - len(seq_indices))
            else:
                seq_indices = seq_indices[:max_len]
                
            data_list.append(seq_indices)
            labels_list.append(is_anomalous)
            
        return torch.tensor(data_list, dtype=torch.long), torch.tensor(labels_list, dtype=torch.float)

    def save_vocab(self, path: str):
        with open(path, 'w') as f:
            json.dump(self.vocab, f)
            
    def load_vocab(self, path: str):
        with open(path, 'r') as f:
            self.vocab = json.load(f)

if __name__ == "__main__":
    # Example usage
    pass
