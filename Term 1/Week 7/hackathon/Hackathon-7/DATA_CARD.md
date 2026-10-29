# Ethical reflection (data card)

*Invasive or Native?* · Hackathon 7 · SDG 15

| | |
|---|---|
| **Source & licence** | 840 research-grade iNaturalist photos, Netherlands only, CC0 / CC BY / CC BY-NC, all photographers credited. No own photos. |
| **Collection** | Selected by hand: max 10 per photographer and 3 per sighting per class; duplicates removed with file hashes and an image fingerprint; 26 rejected after checking every photo by eye. |
| **Labels** | Species, from iNaturalist community votes: reliable, not perfect. |
| **Composition & splits** | 7 species, 90–150 training photos each (760 in total). In Roboflow: 80/15/5 split; flips, ±15° rotation, crop, brightness; no grayscale or 90° rotation, because colour and orientation are real clues. 80 test photos kept outside Roboflow, from other sightings *and* other photographers. |
| **Gaps & biases** | Mostly sharp summer photos of plants in flower; autumn/winter photos only 19% (giant hogweed), 3% (bindweed), 9% (loosestrife), so the model may partly have learned "dead stems = invasive". Photos cluster around popular places. |
| **Results** | Roboflow test split (38 photos): F1 82.5%, precision 86.8%, recall 81%. Our 80 held-out photos: 90% species accuracy; per species 100% (common hogweed, hedge bindweed, Himalayan balsam), 93% (giant hogweed), 80% (other umbellifers, purple loosestrife), 70% (Japanese knotweed). With the safety rules, 0 of 35 invasive plants were called "Native" and 2 of 45 native plants gave a false alarm. |
| **Failure modes** | Hogweed against hogweed (1 of 4 giant hogweeds called common on the Roboflow split; 1 of 15 on our held-out set, where the 20% rule still warned); Japanese knotweed (only 70% right); dead stems and young rosettes; any plant outside the 7 is forced into one of them (e.g. poisonous hemlock, which looks like cow parsley); stem spots lost at 224×224 px. |
| **Intended use** | First check before reporting to Waarneming.nl. **Not** for removing plants without an expert, other species, or use outside the Netherlands. |
| **What could go wrong** | Giant hogweed called "Native" → someone touches it and gets burned (0 of 35 invasive plants in our test, but the test is small). False alarms → wasted municipal time, useful native plants removed. Over-trust → cutting knotweed, which spreads it. |
| **What we did** | 70% "unsure" rule, 20% giant hogweed warning, strict held-out test, expert confirmation via Waarneming.nl before anyone acts. **Next:** more winter photos and an "other plant" class. |
