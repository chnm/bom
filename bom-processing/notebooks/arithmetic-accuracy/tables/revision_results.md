# Revision analysis results

## Figures 4 and 5 annual comparison

- Buried: 110 paired years; Pearson r = 0.915, p = 2.65e-44; 8 fully legible years.
- Plague: 58 paired years; Pearson r = 0.100, p = 0.456; 8 fully legible years.

## Figure 9 replacement

- 90 annual observations; linear slope = -0.436; Pearson r = -0.470; p = 2.88e-06.
- A fitted line and 95% confidence interval were plotted.

## Figure 4 time-series diagnostics

- buried, signed_difference: 5180/5258 weeks observed (98.5%); longest contiguous run 1690; Ljung-Box p = 1.54e-07; ARIMA(2, 0, 2) candidate was inadequate because residual autocorrelation remained (p = 9.76e-05).
- buried, absolute_difference: 5180/5258 weeks observed (98.5%); longest contiguous run 1690; Ljung-Box p = 2.75e-11; ARIMA(1, 0, 2) candidate was inadequate because residual autocorrelation remained (p = 6.66e-05).
- plague, signed_difference: 2601/5258 weeks observed (49.5%); longest contiguous run 898; Ljung-Box p = 1; no ARMA-family model fitted.
- plague, absolute_difference: 2601/5258 weeks observed (49.5%); longest contiguous run 898; Ljung-Box p = 1; no ARMA-family model fitted.
