# Invasive or Native?

**Hackathon 7 "Eyes on Earth" · Roboflow · SDG 15 – Life on Land (target 15.8: invasive alien species)**

**Live app:** https://hackathon-7-u97t5prpmjnmzn3wttrzv9.streamlit.app/

A phone web app for the Netherlands: take or upload a photo of a plant, and it says whether it looks like an **invasive species** or its **native look-alike**. It is a quick first check before reporting a sighting, not a final identification.

## The problem

Giant hogweed, Japanese knotweed and Himalayan balsam spread along Dutch verges, parks and waterways, and each has a harmless native look-alike. Invasive species contributed to **60% of recorded global extinctions** and cost more than **$423 billion a year** ([IPBES, 2023](https://unep.org/resources/report/invasive-alien-species-report)); in the Netherlands they are estimated to cost **€1.1–3.1 billion a year** ([Van der Weijden & Reinhold, 2018](https://edepot.wur.nl/506684)). Giant hogweed has been on the **EU list of invasive species since 2017**, and its sap plus sunlight causes **severe burns** ([Provincie Flevoland, 2022](https://www.flevoland.nl/getmedia/7874573e-3258-4187-b5fd-5e7e4abc9be1/FLE220046-Factsheet-Exoten-Reuzenberenklauw-DV.pdf)). Yet it looks very similar to native common hogweed.

## Who it is for

Volunteers, municipal green-space crews and citizen scientists in the Netherlands who find a plant outdoors with only a phone and need to know: *keep my distance and report it, or leave it?* General plant-ID apps give a species name and treat every mistake as equally bad; this app is trained on exactly the pairs that get confused and deliberately prefers a false alarm over a missed giant hogweed.

## How it works

| Invasive | Native look-alike |
|---|---|
| Giant hogweed | Common hogweed; cow parsley / wild angelica |
| Japanese knotweed | Hedge bindweed |
| Himalayan balsam | Purple loosestrife |

1. **Photo in:** browser camera or upload.
2. **Roboflow model:** a ViT Base classifier scores all 7 species. It learns *species*, not "invasive yes/no", because invasiveness is not visible in a photo.
3. **Safety rules** ([`plantid.py`](plantid.py)): top score below **70%** → *Unsure, do not touch*; giant hogweed **≥ 20%** → always a warning, never "Native".
4. **Output:** **Invasive**, **Native** or **Unsure**, how to recognise the plant, what to do, and a button to report it on [Waarneming.nl](https://waarneming.nl).

**Data:** 840 research-grade iNaturalist photos from the Netherlands, all credited. 760 for training, **80 kept apart** as our own test set from other sightings *and* other photographers.

## Results

On our **80 held-out photos** ([`evaluate.py`](evaluate.py), same safety rules as the app):

* Species accuracy **90% (72/80)**; weakest class Japanese knotweed (70%)
* Invasive plants called "Native": **0 / 35** (3 got "Unsure")
* Giant hogweed warned about: **15 / 15**
* False alarms on native plants: **2 / 45**

With 80 photos this shows a trend, not a guarantee. Details, limitations and risks are in our [ethical reflection / data card](DATA_CARD.md).

## How to run it

Open the **live app** on a phone. Locally: `pip install -r requirements.txt` (Python 3.11+), copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and add a Roboflow API key and model ID, then `streamlit run app.py`. Held-out test: `python evaluate.py path/to/dataset/test` (saves `results.csv`).
