# Final forecasting comparison

Generated draft; pending human review.

All frozen candidates are reported; the downstream producer mapping is separate.
Seasonal Naive outperformed learned models in validation at 14 and 28 days.
Simulated data; December 3–16 had prior validation exposure and full-year EDA inspected the final interval.

| Role | Model | Horizon | Configuration | WAPE | MAE | RMSE | Bias | Status |
|---|---|---:|---|---|---|---|---|---|
| primary | xgboost | 1 | GBM006 | 0.3022886893169333 | 4.687892993927002 | 5.956720003479292 | -2.3674004249572755 | valid |
| primary | xgboost | 7 | GBM009 | 0.21849152311381434 | 24.72624868774414 | 28.19651137486619 | -23.911844451904297 | valid |
| primary | xgboost | 14 | GBM022 | 0.28637579706078414 | 66.6614125366211 | 70.49288687813687 | -66.65070416259766 | valid |
| primary | xgboost | 28 | GBM003 | 0.37086299051211 | 184.5547751464844 | 187.3698328121354 | -184.5547751464844 | valid |
| primary | lightgbm | 1 | GBM018 | 0.30382986353577623 | 4.711793523712817 | 5.976578358817961 | -2.3923449315775596 | valid |
| primary | lightgbm | 7 | GBM011 | 0.21742439002586517 | 24.60548337044711 | 28.08160479602628 | -23.756458303596517 | valid |
| primary | lightgbm | 14 | GBM014 | 0.28685109235950523 | 66.77204987507619 | 70.53393440586665 | -66.77204987507619 | valid |
| primary | lightgbm | 28 | GBM022 | 0.39293633907826025 | 195.53926803354912 | 198.3636891470377 | -195.53926803354912 | valid |
| primary | catboost | 1 | GBM017 | 0.30447905308362017 | 4.721861155220782 | 5.988406610074688 | -2.3284464344212474 | valid |
| primary | catboost | 7 | GBM007 | 0.2175243109686565 | 24.61679122370092 | 28.211859061315142 | -23.7095352935551 | valid |
| primary | catboost | 14 | GBM021 | 0.27827502302528806 | 64.77574675973446 | 68.77769808617174 | -64.77574675973446 | valid |
| primary | catboost | 28 | GBM015 | 0.37388649474359525 | 186.05937969822375 | 189.07602486336256 | -186.05937969822375 | valid |
| supportive | ridge | 1 | fixed | 0.2922003584097735 | 4.531443158218767 | 5.750446412396494 | -1.3424772611033802 | valid |
| supportive | ridge | 7 | fixed | 0.1562215108697059 | 17.67927594210288 | 21.798435394771744 | -12.927662570376956 | valid |
| supportive | ridge | 14 | fixed | 0.1517311025101034 | 35.31935911789183 | 42.352146820802346 | -30.520118164557225 | valid |
| supportive | ridge | 28 | fixed | 0.18041612404340654 | 89.78155830446467 | 102.57361798425538 | -87.73162950566811 | valid |
| supportive | random_forest | 1 | fixed | 0.31204883500988734 | 4.839253333333333 | 6.09423632258838 | -2.42544 | valid |
| supportive | random_forest | 7 | fixed | 0.22055268862811633 | 24.95950666666667 | 28.728220540475913 | -24.12612 | valid |
| supportive | random_forest | 14 | fixed | 0.2894828791055206 | 67.38466666666667 | 71.63812417855608 | -67.38466666666667 | valid |
| supportive | random_forest | 28 | fixed | 0.4021616335366948 | 200.13010666666665 | 203.1580522881412 | -200.13010666666665 | valid |
| simple_baseline | naive | 1 | not_tuned | 0.3941191643022956 | 6.112 | 7.611044606359892 | -0.68 | valid |
| simple_baseline | naive | 7 | not_tuned | 0.2829421744662802 | 32.02 | 40.29049515704666 | -9.372 | valid |
| simple_baseline | naive | 14 | not_tuned | 0.2791696738495378 | 64.984 | 80.42904947840674 | -25.184 | valid |
| simple_baseline | naive | 28 | not_tuned | 0.2849713445168758 | 141.812 | 174.1444802455708 | -82.452 | valid |
| simple_baseline | seasonal_naive | 1 | not_tuned | 0.3930874387412948 | 6.096 | 7.751644986710885 | -1.32 | valid |
| simple_baseline | seasonal_naive | 7 | not_tuned | 0.15827795843347942 | 17.912 | 22.599823008156502 | -9.488 | valid |
| simple_baseline | seasonal_naive | 14 | not_tuned | 0.14785029384472625 | 34.416 | 43.170360202342536 | -25.416 | valid |
| simple_baseline | seasonal_naive | 28 | not_tuned | 0.17464170598590134 | 86.908 | 102.75063016838388 | -82.916 | valid |
