# Supplied baseline v3 wall navigation

The antenna side and motor turn conventions agree. Baseline v2's fixed exploratory oscillation dominated its weak raw odor gradient, while side-ray avoidance could continue steering after the forward path cleared. V3 normalizes the bilateral odor difference, limits oscillatory exploration to very weak odor, and primarily reacts to the forward obstacle ray. Extremely close side rays retain collision avoidance.

Three independent seeds 501–503 completed ten seconds of physical walking toward a food source beyond a 3 mm wall. All three passed the wall's far x coordinate without flipping; all physics remained finite. V2's three failed passage trials remain in `baseline-avoidance-v2.json`. This is a narrow test, not validated food collection, arbitrary maze navigation, predator escape, or full-brain control.

The full-brain controller does not use the supplied odor/wall rule. Its unresolved odor-to-action pathway and failed learning evaluation are unchanged. Controller names and source hashes are now included in new run manifests. The new trials and source are retained in an immutable experiment archive.
