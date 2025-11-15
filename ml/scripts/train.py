import joblib
from sklearn.ensemble import RandomForestClassifier
import numpy as np

# Dummy features: mean pixel intensity and std deviation
X = np.array([
    [120, 55],
    [180, 30],
    [90, 70],
    [200, 20],
])
y = [0, 1, 0, 1]  # 0 = normal, 1 = accident

model = RandomForestClassifier()
model.fit(X, y)

joblib.dump(model, "../model/accident_model.pkl")
print("Model trained & saved in model/accident_model.pkl")

