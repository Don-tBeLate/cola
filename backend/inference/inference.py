from pathlib import Path
from transformers import Wav2Vec2ForSequenceClassification, Wav2Vec2FeatureExtractor
import torch
import torch.nn.functional as F
import torchaudio
import os

def load_and_preprocess_audio(file_path):
    waveform, sample_rate = torchaudio.load(file_path)
    resampler = torchaudio.transforms.Resample(sample_rate, feature_extractor.sampling_rate)
    waveform = resampler(waveform)

    if waveform.shape[0] > 1:
        waveform = waveform.mean(0, keepdim=True)

    return waveform.squeeze().numpy()

def predict_top3(file_path):
    waveform = load_and_preprocess_audio(file_path)
    inputs = feature_extractor(waveform, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        logits = model(**inputs).logits

    probabilities = F.softmax(logits, dim=-1).squeeze()

    return torch.topk(probabilities, k=3)

def print_result(top_probs, top_indices):
    for i in range(3):
        index = top_indices[i].item()
        prob = top_probs[i].item() * 100
        label = id2label[index]
        print(f"{i+1}. {label}: {prob:.2f}%")

# 0. GPU / CPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 1. model choose
checkpoint = 105
checkpoint_dir = f"C:/cola/backend/inference/checkpoint-{checkpoint}"
## 경로도 바꾸시오!!!

# 2. model on
feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained(checkpoint_dir)
model = Wav2Vec2ForSequenceClassification.from_pretrained(checkpoint_dir)

id2label = model.config.id2label
label2id = model.config.label2id

# 3. model to device
model.to(device)

# 4. predict
audio_file = "C:/cola/backend/inference/부산대구사투리2s.wav"   # 여기 파일 넣기!!!!!
probs, idxs = predict_top3(audio_file)
print_result(probs, idxs)
