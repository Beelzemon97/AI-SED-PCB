# Model

- `modeloCWRU_corregido.py`: training script. CWRU drive-end data (12 kHz) resampled to 13.33 kHz, 1024-sample windows with 50% overlap, 22 features (RMS, peak, crest factor, kurtosis, skewness, standard deviation, log10 energy in 16 FFT bands).
- `modelo_rodamientos_corregido.tflite`: exported TensorFlow Lite model (8 KB).
- `modelo_pesos.h`: weights as C arrays used by `firmware/src/ai_pipeline.c`.

Network: MLP 22 → 32 → 16 → 4 (ReLU, softmax), 1,332 parameters, Adam, 40 epochs, class weights.

Results: trained on loads 0-2 HP, tested on 3 HP (unseen): 100% on 1,843 clean windows; robust to noise (SNR 20, 5, 0 dB) and gain changes. Laboratory data only: validation on a real motor is pending.
