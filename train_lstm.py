# train_lstm.py
import os
import pandas as pd
import pickle
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense
from sklearn.model_selection import train_test_split

# Load dataset
df = pd.read_csv("fake_or_real_news.csv")  # must have 'text' and 'label' columns
X = df['text'].values
y = df['label'].map({'FAKE':0,'REAL':1}).values

# Tokenizer
tokenizer = Tokenizer(num_words=5000)
tokenizer.fit_on_texts(X)
X_seq = tokenizer.texts_to_sequences(X)
X_pad = pad_sequences(X_seq, maxlen=300)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X_pad, y, test_size=0.2, random_state=42)

# Build model
model = Sequential([
    Embedding(input_dim=5000, output_dim=128, input_length=300),
    LSTM(128, dropout=0.2, recurrent_dropout=0.2),
    Dense(1, activation='sigmoid')
])
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

# Train
model.fit(X_train, y_train, epochs=5, batch_size=64, validation_split=0.1)

# Make sure model folder exists
if not os.path.exists("model"):
    os.makedirs("model")

# Save model and tokenizer
model.save("model/fake_news_lstm.h5")
with open("model/tokenizer.pkl", "wb") as f:
    pickle.dump(tokenizer, f)

print("✅ Model and tokenizer saved!")