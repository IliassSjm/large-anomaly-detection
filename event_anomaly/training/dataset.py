
import torch
from torch.utils.data import Dataset
import json
from ..data.preprocess import LogPreprocessor

class LogDataset(Dataset):
    def __init__(self, data_path, vocab_path=None, max_len=20, is_train=True):
        with open(data_path, 'r') as f:
            self.raw_data = json.load(f)
            
        self.preprocessor = LogPreprocessor()
        if vocab_path and not is_train:
            self.preprocessor.load_vocab(vocab_path)
        else:
            self.preprocessor.fit(self.raw_data)
            if vocab_path:
                self.preprocessor.save_vocab(vocab_path)
                
        self.X, self.y = self.preprocessor.transform(self.raw_data, max_len=max_len)
        
    def __len__(self):
        return len(self.X)
    
    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]
