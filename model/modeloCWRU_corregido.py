"""Copia CORREGIDA del modelo CWRU (el original no se toca).
Cambios respecto a modeloCWRU.py:
 1. Carga de .mat por numero de archivo (99.mat traia tambien las claves de 98.mat).
 2. Remuestreo de CWRU (12 kHz) a FS_OBJ = 13.333 kHz = sensor IIS3DWB (26.667 kHz) / 2,
    para que el firmware pueda usar exactamente la misma frecuencia.
 3. Clases balanceadas (pesos de clase) y metricas por clase.
 4. Validacion dejando una carga fuera a la vez.
 5. Exporta pesos a C (modelo_pesos.h) ademas de .h5/.tflite si hay TensorFlow.
"""
import re, sys, numpy as np, scipy.io as sio
from scipy.stats import kurtosis, skew
from scipy.signal import resample_poly
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay
from sklearn.utils.class_weight import compute_class_weight
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

DATA_DIR = "cwru"
FS_CWRU = 12000
FS_OBJ  = 40000 / 3        # 13333.33 Hz = 26666.67 / 2 (sensor con decimacion entre 2)
UP, DOWN = 10, 9           # 12000 * 10/9 = 13333.3
WIN, STEP, N_BANDS = 1024, 512, 16
FILES = {"sano": [97, 98, 99, 100], "pista_int": [105, 106, 107, 108],
         "bola": [118, 119, 120, 121], "pista_ext": [130, 131, 132, 133]}
CLASSES = list(FILES)

def load_signal(num):
    m = sio.loadmat(f"{DATA_DIR}/{num}.mat")
    key = [k for k in m if k.startswith("X%03d" % num) and "DE_time" in k][0]   # FIX 99.mat
    return resample_poly(m[key].ravel(), UP, DOWN)                              # 12k -> 13.33k

def features(w):
    w = w - np.mean(w)
    rms = np.sqrt(np.mean(w**2)); peak = np.max(np.abs(w))
    td = [rms, peak, peak/(rms+1e-12), kurtosis(w), skew(w), np.std(w)]
    spec = np.abs(np.fft.rfft(w*np.hanning(WIN)))/WIN
    fd = [np.log10(np.sum(b**2) + 1e-12) for b in np.array_split(spec[1:], N_BANDS)]   # FIX: energia en log10 (robusta a ruido/ganancia)
    return np.array(td+fd, dtype=np.float32)

def build(noise_db=None, gain=1.0, seed=0):
    """noise_db: SNR (dB) del ruido blanco anadido a cada archivo; gain: factor de ganancia."""
    rng = np.random.default_rng(seed)
    X, y, load = [], [], []
    for ci, c in enumerate(CLASSES):
        for ld, n in enumerate(FILES[c]):
            s = load_signal(n) * gain
            if noise_db is not None:
                s = s + rng.normal(0, np.sqrt(np.mean(s**2) / 10**(noise_db/10)), len(s))
            for i in range(0, len(s)-WIN+1, STEP):
                X.append(features(s[i:i+WIN])); y.append(ci); load.append(ld)
    return np.array(X), np.array(y), np.array(load)

# Aumento de datos: combinaciones (SNR dB, ganancia) que se anaden al entrenamiento
AUG = [(None,1.0),(20,1.0),(10,1.0),(5,1.0),(None,0.5),(None,2.0),(10,0.7),(10,1.5)]
def build_aug(loads):
    Xs, ys = [], []
    for k,(db,g) in enumerate(AUG):
        X, y, l = build(db, g, seed=k); m = np.isin(l, loads); Xs.append(X[m]); ys.append(y[m])
    return np.vstack(Xs), np.concatenate(ys)

def train(Xtr, ytr):
    sc = StandardScaler().fit(Xtr); Z = sc.transform(Xtr)
    cw = compute_class_weight("balanced", classes=np.arange(4), y=ytr)
    rng = np.random.default_rng(0); idx = rng.permutation(len(ytr)); Z, ytr = Z[idx], ytr[idx]
    try:
        import tensorflow as tf
        tf.random.set_seed(0)
        m = tf.keras.Sequential([tf.keras.layers.Input(shape=(22,)),
            tf.keras.layers.Dense(32, activation="relu"), tf.keras.layers.Dense(16, activation="relu"),
            tf.keras.layers.Dense(4, activation="softmax")])
        m.compile("adam", "sparse_categorical_crossentropy", metrics=["accuracy"])
        m.fit(Z, ytr, epochs=40, batch_size=64, validation_split=0.2, class_weight=dict(enumerate(cw)), verbose=2)
        return sc, m, (lambda X: m.predict(sc.transform(X), verbose=0).argmax(1)), "keras"
    except ImportError:
        from sklearn.neural_network import MLPClassifier
        w = cw[ytr]; m = MLPClassifier((32,16), max_iter=300, random_state=0)
        # sklearn no admite sample_weight en MLP: se sobremuestrea para balancear
        reps = np.round(cw/cw.min()).astype(int); ii = np.concatenate([np.repeat(np.where(ytr==c)[0], reps[c]) for c in range(4)])
        m.fit(Z[ii], ytr[ii])
        return sc, m, (lambda X: m.predict(sc.transform(X))), "sklearn"

if __name__ == "__main__":
    print("FS_OBJ =", round(FS_OBJ,1), "Hz | aumento:", AUG)
    print("== Validacion dejando una carga fuera (con aumento) ==")
    Xc, yc, lc = build()
    for k in range(4):
        Xa, ya = build_aug([l for l in range(4) if l != k])
        sc, m, pr, kind = train(Xa, ya); print(f"prueba carga {k} HP: exactitud {np.mean(pr(Xc[lc==k])==yc[lc==k]):.4f}")
    Xa, ya = build_aug([0,1,2]); sc, m, pr, kind = train(Xa, ya)
    print("\n== Entrena 0-2 HP (aumentado) / prueba 3 HP (", kind, ") ==")
    te = lc == 3; p = pr(Xc[te]); print(classification_report(yc[te], p, target_names=CLASSES, digits=4))
    ConfusionMatrixDisplay(confusion_matrix(yc[te], p), display_labels=CLASSES).plot(cmap="Blues")
    plt.savefig("matriz_confusion_corregida.png", dpi=150, bbox_inches="tight")
    print("== Robustez (prueba 3 HP, datos nuevos nunca vistos) ==")
    for db,g in [(None,1.0),(20,1.0),(10,1.0),(5,1.0),(0,1.0),(None,0.5),(None,2.0)]:
        X, y, l = build(db, g, seed=99); print(f"SNR={db} dB, ganancia x{g}: {np.mean(pr(X[l==3])==y[l==3]):.3f}")
    np.savez("scaler_corregido.npz", mean=sc.mean_, scale=sc.scale_, fs=FS_OBJ, win=WIN)
    if kind == "keras":
        import tensorflow as tf
        m.save("modelo_rodamientos_corregido.h5")
        open("modelo_rodamientos_corregido.tflite","wb").write(tf.lite.TFLiteConverter.from_keras_model(m).convert())
        Ws = [(l.get_weights()) for l in m.layers if l.get_weights()]
    else:
        Ws = [[m.coefs_[i], m.intercepts_[i]] for i in range(3)]
    with open("modelo_pesos.h", "w") as f:
        f.write(f"// MLP 22-32-16-4, float32. fs={FS_OBJ:.2f} Hz, ventana {WIN}\n")
        f.write("static const float MEAN[22]={%s};\nstatic const float SCALE[22]={%s};\n" % (
            ",".join(f"{v:.8e}f" for v in sc.mean_), ",".join(f"{v:.8e}f" for v in sc.scale_)))
        for i,(W,b) in enumerate(Ws):
            f.write(f"static const float W{i+1}[{W.shape[0]}][{W.shape[1]}]={{{','.join('{'+','.join(f'{v:.8e}f' for v in r)+'}' for r in W)}}};\n")
            f.write(f"static const float B{i+1}[{len(b)}]={{{','.join(f'{v:.8e}f' for v in b)}}};\n")
    print("Guardado: scaler_corregido.npz, modelo_pesos.h, matriz_confusion_corregida.png", "(+h5/tflite)" if kind=="keras" else "(sin TF: sin h5/tflite)")
