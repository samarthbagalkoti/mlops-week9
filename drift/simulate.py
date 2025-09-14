import os, time, random
import numpy as np
import pandas as pd
from sklearn.datasets import make_classification

DATA_DIR = os.environ.get("DATA_DIR", "/data")
REF_PATH = os.path.join(DATA_DIR, "reference.csv")
CUR_PATH = os.path.join(DATA_DIR, "current.csv")

def make_batch(n_samples=800, shift=0.0, seed=None):
    rng = np.random.RandomState(seed)
    X, y = make_classification(
        n_samples=n_samples, n_features=6, n_informative=4, n_redundant=0,
        class_sep=1.2 - shift, random_state=seed
    )
    # inject controlled mean shift on first two features
    X[:, 0] += shift * 0.8
    X[:, 1] += shift * 0.5
    df = pd.DataFrame(X, columns=[f"f{i}" for i in range(X.shape[1])])
    df["target"] = y
    return df

def init_reference():
    if not os.path.exists(REF_PATH):
        ref = make_batch(n_samples=2000, shift=0.0, seed=42)
        ref.to_csv(REF_PATH, index=False)
        print(f"[sim] wrote reference: {REF_PATH}")

def write_current(shift, n=400):
    cur = make_batch(n_samples=n, shift=shift, seed=random.randint(0, 10_000))
    cur.to_csv(CUR_PATH, index=False)
    print(f"[sim] wrote current (shift={shift:.2f}) rows={n}")

def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    init_reference()

    # Loop: alternate low-drift ↔ high-drift every ~30s
    while True:
        # ~30s “healthy”
        for _ in range(3):
            write_current(shift=0.05, n=500)
            time.sleep(10)

        # ~30s “drifted”
        for _ in range(3):
            write_current(shift=0.6, n=500)
            time.sleep(10)

if __name__ == "__main__":
    main()

