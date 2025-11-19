
import torch
from torch.utils.data import DataLoader
from sklearn.metrics import roc_auc_score, classification_report
import json
from ..config import *
from ..models.sequence_model import LogAnomalyModel
from .dataset import LogDataset

def evaluate():
    # Load Data (using same data for simplicity, ideally should be split)
    dataset = LogDataset(
        "event_anomaly/data/processed/logs.json", 
        vocab_path="event_anomaly/artifacts/vocab.json",
        max_len=SEQUENCE_LENGTH,
        is_train=False
    )
    dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=False)
    
    # Load Model
    vocab_size = len(dataset.preprocessor.vocab)
    model = LogAnomalyModel(vocab_size, EMBEDDING_DIM, HIDDEN_DIM, NUM_LAYERS, DROPOUT)
    model.load_state_dict(torch.load(MODEL_SAVE_PATH))
    model.eval()
    
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        for X_batch, y_batch in dataloader:
            outputs = model(X_batch).squeeze()
            all_preds.extend(outputs.tolist())
            all_labels.extend(y_batch.tolist())
            
    # Metrics
    try:
        auc = roc_auc_score(all_labels, all_preds)
        print(f"ROC AUC: {auc:.4f}")
    except:
        print("Could not calculate AUC (maybe only one class present)")
        
    # Binary classification metrics (threshold 0.5)
    binary_preds = [1 if p > 0.5 else 0 for p in all_preds]
    print(classification_report(all_labels, binary_preds))
    
    results = {
        "auc": auc if 'auc' in locals() else 0.0,
        "report": classification_report(all_labels, binary_preds, output_dict=True)
    }
    
    with open("event_anomaly/artifacts/eval_results.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    evaluate()
