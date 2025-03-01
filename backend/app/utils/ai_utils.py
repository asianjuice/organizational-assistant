# backend/app/utils/ai_utils.py

from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pandas as pd
from datetime import datetime

# Sample data for training the model
def generate_sample_data():
    data = {
        "days_until_deadline": [1, 5, 10, 2, 7, 3],
        "task_length": [2, 5, 1, 3, 4, 2],  # Estimated task length in hours
        "priority": ["high", "medium", "low", "high", "medium", "high"],  # Target variable
    }
    return pd.DataFrame(data)

# Train a decision tree model
def train_priority_model():
    # Generate sample data
    df = generate_sample_data()

    # Convert priority labels to numerical values
    priority_map = {"high": 2, "medium": 1, "low": 0}
    df["priority"] = df["priority"].map(priority_map)

    # Features and target variable
    X = df[["days_until_deadline", "task_length"]]
    y = df["priority"]

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train the model
    model = DecisionTreeClassifier()
    model.fit(X_train, y_train)

    # Evaluate the model
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model accuracy: {accuracy * 100:.2f}%")

    return model

# Predict task priority
def predict_task_priority(model, days_until_deadline: int, task_length: int):
    priority_map = {2: "high", 1: "medium", 0: "low"}
    prediction = model.predict([[days_until_deadline, task_length]])
    return priority_map[prediction[0]]