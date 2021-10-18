import numpy as np
import pandas as pd

# the following implementation is based on a book 'real-world-machine-learning-1st-henrik-brink'

def full_machine(train_features, train_target, test_features):

    from sklearn.linear_model import LogisticRegression as Model

    def cat_to_num(data):
        categories = np.unique(data)
        features = []
        for cat in categories:
            binary = (data == cat)
            features.append(binary.astype("int"))
        return features[0]

    def normalize_feature(data, f_min=-1.0, f_max=1.0):
        d_min, d_max = min(data), max(data)
        factor = (f_max - f_min) / (d_max - d_min)
        normalized = f_min + (data - d_min) * factor
        return normalized, factor

    def train(features, target):
        model = Model()
        model.fit(features, target)
        return model

    def predict(model, new_features):
        preds = model.predict(new_features)
        return preds

    model = train(train_features, train_target)
    predictions = predict(model, test_features)

    return predictions

