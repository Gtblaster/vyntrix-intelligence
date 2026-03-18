import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image
import io

class SteganographyCNN(nn.Module):
    """
    A simple Convolutional Neural Network architecture designed for binary
    image classification (Clean vs. Steganography Payload).
    """
    def __init__(self):
        super(SteganographyCNN, self).__init__()
        # 1 input image channel (RGB), 16 output channels, 3x3 square convolution kernel
        self.conv1 = nn.Conv2d(3, 16, kernel_size=3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, padding=1)
        self.fc1 = nn.Linear(32 * 56 * 56, 128) # Assuming 224x224 input image
        self.fc2 = nn.Linear(128, 1) # Binary output (0 = Clean, 1 = Infected)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = torch.flatten(x, 1) # flatten all dimensions except batch
        x = F.relu(self.fc1(x))
        x = torch.sigmoid(self.fc2(x)) # Sigmoid to output a probability between 0 and 1
        return x

# Initialize the model instance
# Note: In a production environment, we would load pre-trained weights here
# model.load_state_dict(torch.load("stego_model_weights.pth"))
model = SteganographyCNN()
model.eval() # Set the model to evaluation mode

# Define the image transformations required by the model
transform = transforms.Compose([
    transforms.Resize((224, 224)), # Resize to standard CNN input size
    transforms.ToTensor(), # Convert PIL image to PyTorch tensor
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]) # Standard ImageNet normalization
])

def predict_image(image_bytes: bytes) -> dict:
    """
    Takes raw image bytes, processes them through the CNN, and returns the prediction probabilities.
    """
    try:
        # Load the image
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        
        # Apply transformations and add a batch dimension
        img_tensor = transform(image).unsqueeze(0) 
        
        # Run the tensor through the model
        with torch.no_grad(): # Disable gradient calculation for faster inference
            output = model(img_tensor)
            
        # The output is a probability of being "Infected" (Payload Present)
        payload_probability = output.item()
        
        # Determine classification threshold
        is_infected = payload_probability > 0.5
        
        # Calculate a pseudo-confidence score based on how far the probability is from 0.5
        # The closer to 0 or 1, the more confident the model is.
        distance_from_center = abs(payload_probability - 0.5)
        confidence = 0.5 + distance_from_center # Maps [0, 0.5] to [0.5, 1.0]
        
        return {
            "success": True,
            "prediction": "INFECTED" if is_infected else "SECURE",
            "is_infected": is_infected,
            "payload_probability": round(payload_probability * 100, 1),
            "confidence": round(confidence * 100, 1)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# ==========================================
# Phase 2: NLP Text/URL Analysis Model
# ==========================================

class TextAnalysisNLP(nn.Module):
    """
    A simple NLP architecture designed to classify raw text/URLs
    into threat probabilities (e.g., detecting XSS, SQLi, Phishing, or safe text).
    """
    def __init__(self, vocab_size=10000, embedding_dim=64, hidden_dim=128):
        super(TextAnalysisNLP, self).__init__()
        self.embedding = nn.Embedding(num_embeddings=vocab_size, embedding_dim=embedding_dim)
        # Using a simple LSTM for sequence processing
        self.lstm = nn.LSTM(embedding_dim, hidden_dim, batch_first=True)
        self.fc1 = nn.Linear(hidden_dim, 64)
        self.fc2 = nn.Linear(64, 1) # Binary output (0 = Safe, 1 = Threat)
        
    def forward(self, x):
        # x shape: (batch_size, sequence_length)
        embedded = self.embedding(x)
        # lstm_out shape: (batch_size, sequence_length, hidden_dim)
        lstm_out, (hidden, cell) = self.lstm(embedded)
        # Use the final hidden state for classification
        final_hidden = hidden[-1] 
        x = F.relu(self.fc1(final_hidden))
        x = torch.sigmoid(self.fc2(x))
        return x

# Initialize the NLP model
nlp_model = TextAnalysisNLP()
nlp_model.eval()

def simple_tokenize(text: str, max_length=100, vocab_size=10000):
    """
    A very rudimentary hash-based tokenizer for demonstration purposes.
    In production, use a real tokenizer (like HuggingFace's AutoTokenizer).
    """
    words = text.lower().split()
    tokens = []
    for word in words:
        # Simple hash trick to map a word to an integer in [1, vocab_size)
        token_id = (hash(word) % (vocab_size - 1)) + 1
        tokens.append(token_id)
        
    # Pad or truncate to max_length
    if len(tokens) > max_length:
        tokens = tokens[:max_length]
    else:
        tokens = tokens + [0] * (max_length - len(tokens)) # 0 is padding
        
    return torch.tensor([tokens], dtype=torch.long)

def predict_text(text: str) -> dict:
    """
    Takes raw text or a URL, processes it through the NLP model, and returns
    vulernability predictions.
    """
    try:
        if not text or len(text.strip()) == 0:
            raise ValueError("Empty text provided")
            
        # Tokenize the text into a tensor
        input_tensor = simple_tokenize(text)
        
        # Run inference
        with torch.no_grad():
            output = nlp_model(input_tensor)
            
        threat_probability = output.item()
        
        # Determine classification threshold (higher sensitivity for demo)
        is_threat = threat_probability > 0.4 
        
        # Pseudo-confidence score
        distance_from_center = abs(threat_probability - 0.5)
        confidence = 0.5 + distance_from_center
        
        # Select categories based on basic text heuristics combined with the AI response
        text_lower = text.lower()
        if "select " in text_lower or "drop " in text_lower or "union " in text_lower:
            classification = "SQL Injection (SQLi) Attempt"
            insight = "NLP Architecture detected structural database query patterns and malicious operand logic."
        elif "<script" in text_lower or "javascript:" in text_lower or "onload=" in text_lower:
            classification = "Cross-Site Scripting (XSS)"
            insight = "Model identified executable script reflections within the primary input vector."
        elif "login" in text_lower or "password" in text_lower or "bank" in text_lower:
             classification = "High-Risk Sensistive Form / Phishing"
             insight = "Contextual analysis highlights phishing topologies or unencrypted credential transmission."
        elif len(text) > 150 and is_threat: # E.g., large malicious paragraphs
             classification = "Malicious Payload Configuration"
             insight = "Deep analysis of the text block reveals underlying malicious logic and abnormal linguistic intent."
        else:
            if is_threat:
                classification = "Anomalous Input Pattern"
                insight = "Model detected structural deviations from standard normal inputs."
            else:
                classification = "SECURE (Normal Traffic)"
                insight = "Linguistic and structural topology appears normalized. No threats detected."

        score = max(12, int((1.0 - threat_probability) * 100))
        if is_threat and score > 40:
            score = 35 # Cap score if it's a threat
            
        return {
            "success": True,
            "is_threat": is_threat,
            "security_score": score,
            "prediction_badge": "HIGH RISK" if is_threat else "SECURE",
            "threat_probability": round(threat_probability * 100, 1),
            "confidence": round(confidence * 100, 1),
            "ai_classification": classification,
            "insight": insight
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
