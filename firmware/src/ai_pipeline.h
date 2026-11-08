/*
 * ai_pipeline.h - Bearing-fault diagnosis pipeline (AI-SED 2026, ITESCA PCB Lab)
 *
 * One window of 1024 samples (13.333 kHz) -> 22 features -> MLP 22-32-16-4 -> class.
 * Pure C99, no dynamic memory, float32. Runs on the STM32F411CE (Cortex-M4F)
 * and on a PC (for testing against the Python reference).
 *
 * On the STM32 define AI_USE_CMSIS_DSP to use arm_rfft_fast_f32 (hardware FPU
 * and DSP instructions); without it a portable radix-2 FFT is used.
 */
#ifndef AI_PIPELINE_H
#define AI_PIPELINE_H

#ifdef __cplusplus
extern "C" {
#endif

#define AI_WIN        1024   /* samples per window                      */
#define AI_N_FEAT     22     /* 6 time-domain + 16 frequency-band energy */
#define AI_N_BANDS    16
#define AI_N_CLASSES  4

typedef enum {
    AI_CLASS_HEALTHY = 0,
    AI_CLASS_INNER_RACE = 1,
    AI_CLASS_BALL = 2,
    AI_CLASS_OUTER_RACE = 3
} ai_class_t;

/* Computes the 22 features of one window. 'window' is not modified. */
void ai_features(const float *window, float *feat /* [AI_N_FEAT] */);

/* Runs the MLP on 22 raw (unscaled) features. Returns the winning class and
 * writes the softmax probabilities to prob[4] (may be NULL). */
ai_class_t ai_classify_features(const float *feat, float *prob);

/* Convenience: window -> class (+ confidence in prob[]). */
ai_class_t ai_diagnose(const float *window, float *prob);

#ifdef __cplusplus
}
#endif
#endif /* AI_PIPELINE_H */
