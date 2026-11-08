/* Compares the C pipeline against the Python reference (data/ref.bin). */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "../src/ai_pipeline.h"

int main(void)
{
    FILE *f = fopen("data/ref.bin", "rb");
    if (!f) { puts("data/ref.bin not found (run test/export_ref.py first)"); return 1; }
    int n; fread(&n, 4, 1, f);
    float *W = malloc((size_t)n * AI_WIN * 4), *F = malloc((size_t)n * AI_N_FEAT * 4);
    int *Y = malloc(n * 4), *P = malloc(n * 4), *S = malloc(n * 4);
    fread(W, 4, (size_t)n * AI_WIN, f); fread(Y, 4, n, f);
    fread(F, 4, (size_t)n * AI_N_FEAT, f); fread(P, 4, n, f); fread(S, 4, n, f);
    fclose(f);

    const char *name[] = {"clean", "snr10", "snr0", "gain0.5", "gain2"};
    int tot[5] = {0}, okc[5] = {0}, okpy[5] = {0}, agree[5] = {0};
    double worst_rel[AI_N_FEAT] = {0}, worst_abs[AI_N_FEAT] = {0};

    for (int i = 0; i < n; i++) {
        float feat[AI_N_FEAT], prob[4];
        ai_features(&W[(size_t)i * AI_WIN], feat);
        for (int k = 0; k < AI_N_FEAT; k++) {
            double ref = F[(size_t)i * AI_N_FEAT + k], d = fabs(feat[k] - ref);
            double rel = d / (fabs(ref) > 1e-3 ? fabs(ref) : 1e-3);
            if (d > worst_abs[k]) worst_abs[k] = d;
            if (rel > worst_rel[k]) worst_rel[k] = rel;
        }
        int c = ai_classify_features(feat, prob);
        int s = S[i];
        tot[s]++; okc[s] += (c == Y[i]); okpy[s] += (P[i] == Y[i]); agree[s] += (c == P[i]);
    }
    puts("Scenario  windows  C-acc    Python-acc  C==Python");
    for (int s = 0; s < 5; s++)
        printf("%-8s  %5d    %6.2f%%  %6.2f%%     %d/%d\n", name[s], tot[s],
               100.0 * okc[s] / tot[s], 100.0 * okpy[s] / tot[s], agree[s], tot[s]);
    double mr = 0; int mk = 0;
    for (int k = 0; k < AI_N_FEAT; k++) if (worst_rel[k] > mr) { mr = worst_rel[k]; mk = k; }
    printf("Largest relative feature error (all windows): %.2e (feature %d)\n", mr, mk);
    return 0;
}
