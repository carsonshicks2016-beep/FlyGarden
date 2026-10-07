# Background registration screen

The v4 prototype estimates background motion from image features using forward/backward optical-flow consistency and a robust projective fit. Visible-self pixels are excluded. Ambiguous fits are exposed and suppress activity; they do not imply a quiet world. Parameters were frozen before replaying the two preserved moving-body eye streams.

Both streams yielded zero pre/post-cue false signals, but also zero intended looming signals. Only5/120 frames per eye passed registration in the left run;2/120 and3/120 passed in the right run. This FAILS the combined signal/specificity requirement. Suppressing every response is not an accepted repair. The encoder is not promoted, no neural runs were repeated, and evaluation seeds remain untouched.

OpenCV headless4.13.0.92 was pinned without changing the existing numerical dependencies. The environment's80 installed packages pass dependency compatibility checking. Static state restoration and explicit invalid-fit behavior tests pass, establishing implementation behavior only.

Next is testing the same registration hypothesis on the cameras' native rectilinear output and preserving its failure modes. The current test uses fisheye-corrected images, while the fitted projective transform is only an approximation there. Further native confounds and useful-cue response must pass before controller integration or held-out brain evaluation.
