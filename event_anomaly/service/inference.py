
import torch
import json
import os
from ..models.sequence_model import LogAnomalyModel
from ..data.preprocess import LogPreprocessor
from ..config import *

class InferenceService:
    def __init__(self, model_path=MODEL_SAVE_PATH, vocab_path="event_anomaly/artifacts/vocab.json"):
        self.preprocessor = LogPreprocessor()
        if os.path.exists(vocab_path):
            self.preprocessor.load_vocab(vocab_path)
        else:
            # Fallback or error
            print("Warning: Vocab not found, using empty vocab")
            
        vocab_size = len(self.preprocessor.vocab)
        self.model = LogAnomalyModel(vocab_size, EMBEDDING_DIM, HIDDEN_DIM, NUM_LAYERS, DROPOUT)
        
        if os.path.exists(model_path):
            self.model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
            self.model.eval()
        else:
            print("Warning: Model not found")
            
        self.threshold = 0.5

    def score_sequence(self, log_sequence: list) -> dict:
        # log_sequence is a list of dicts
        # Transform single sequence
        # We need to wrap it in a list for the preprocessor
        X, _ = self.preprocessor.transform([log_sequence], max_len=SEQUENCE_LENGTH)
        
        with torch.no_grad():
            score = self.model(X).item()
            
        is_anomalous = score > self.threshold
        
        return {
            "anomaly_score": score,
            "is_anomalous": is_anomalous,
            "threshold": self.threshold
        }
