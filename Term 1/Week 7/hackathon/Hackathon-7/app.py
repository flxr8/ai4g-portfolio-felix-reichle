"""Invasive or Native? — a field ID helper for Dutch volunteers.

Run locally:   streamlit run app.py
Needs two secrets: ROBOFLOW_API_KEY and ROBOFLOW_MODEL_ID (see README).
"""

import hashlib
import os

import streamlit as st

import plantid

try:  # iPhone photos can arrive as HEIC; this lets Pillow open them.
    from pillow_heif import register_heif_opener
    register_heif_opener()
except ImportError:
    pass

st.set_page_config(page_title="Invasive or Native?", page_icon="🌿",
                   layout="centered")

st.markdown(
    """
    <style>
      .block-container {padding-top: 1.5rem; padding-bottom: 3rem; max-width: 720px;}
      h1 {font-size: clamp(1.9rem, 7vw, 2.6rem) !important; padding-top: 0 !important;}
      .verdict {font-size: 1.6rem; font-weight: 700; margin: 0;}
      .species {font-size: 1.05rem; margin: .25rem 0 0;}
      .muted {opacity: .75; font-size: .9rem;}
      div[data-testid="stTabs"] button {font-size: 1rem; padding: .6rem 1rem;}
    </style>
    """,
    unsafe_allow_html=True,
)


def get_setting(name: str) -> str | None:
    try:
        if name in st.secrets:
            return st.secrets[name]
    except Exception:  # no secrets file at all
        pass
    return os.environ.get(name)


@st.cache_data(show_spinner=False, max_entries=50)
def run_model(image_bytes: bytes, model_id: str, api_key: str):
    img = plantid.prepare_image(image_bytes)
    return plantid.classify(img, model_id, api_key)


def render_result(v: plantid.Verdict, photo=None) -> None:
    """Show the verdict, the photo, species info and next steps."""
    info = plantid.SPECIES.get(v.top_class or "", {})
    pct = f"{v.top_confidence:.0%}"

    if v.kind == "invasive":
        box = st.error
        title = "Invasive"
        line = f"Looks like **{info.get('name')}** ({pct} sure)."
    elif v.kind == "native":
        box = st.success
        title = "Native"
        line = f"Looks like **{info.get('name')}** ({pct} sure)."
    elif v.top_class is None:
        box = st.warning
        title = "Unsure, do not touch"
        line = "The model did not recognise any of the seven plants it knows."
    else:
        box = st.warning
        title = "Unsure, do not touch"
        line = (f"Best guess: **{info.get('name', 'unknown')}**, but only {pct} sure."
                if not v.hogweed_alert or v.top_class == "giant_hogweed" else
                f"Best guess: **{info.get('name', 'unknown')}** ({pct}), "
                "but this could also be giant hogweed.")
    box(f"### {title}\n{line}")

    if v.hogweed_alert:
        gh = dict(v.scores).get("giant_hogweed", 0)
        st.error(
            f"**Possible giant hogweed ({gh:.0%}).** Do not touch this plant. "
            "Its sap causes severe burns in sunlight. Keep children and pets away."
        )

    if photo is not None:
        st.image(photo, width=260, caption="Your photo")

    if info:
        st.markdown(f"#### {info['name']}")
        st.markdown(f"*{info['latin']}* · Dutch: {info['dutch']}")
        st.markdown(f"**How to recognise it:** {info['tip']}")
        st.markdown(f"**What to do:** {info['action']}")

    if v.kind in ("invasive", "unsure") or v.hogweed_alert:
        st.markdown("#### Report it")
        st.markdown(
            "Report the sighting on Waarneming.nl with your photo and location, "
            "or contact your municipality. An expert can then confirm the ID."
        )
        st.link_button("Report on Waarneming.nl", plantid.REPORT_URL,
                       use_container_width=True)
    if v.kind == "unsure":
        st.markdown("Tip: take a closer photo of the **leaves or the stem**, "
                    "in good light, and try again.")

    with st.expander("All scores"):
        for cls, score in v.scores:
            name = plantid.SPECIES[cls]["name"]
            tag = "invasive" if cls in plantid.INVASIVE else "native"
            st.markdown(f"{name} <span class='muted'>({tag})</span> — {score:.0%}",
                        unsafe_allow_html=True)
            st.progress(min(max(score, 0.0), 1.0))


def main() -> None:
    st.title("Invasive or Native?")
    st.write(
        "A quick first check for volunteers and green-space crews in the "
        "Netherlands. Take or upload a photo of a plant to see whether it "
        "looks like an invasive species or a native look-alike."
    )

    api_key = get_setting("ROBOFLOW_API_KEY")
    model_id = get_setting("ROBOFLOW_MODEL_ID")
    if not api_key or not model_id:
        st.error("The app is not set up yet: ROBOFLOW_API_KEY and "
                 "ROBOFLOW_MODEL_ID are missing. See the README.")
        st.stop()

    tab_cam, tab_up = st.tabs(["Take a photo", "Upload a photo"])
    with tab_cam:
        cam = st.camera_input("Point your camera at the plant",
                              label_visibility="collapsed")
        st.caption("Allow camera access when your browser asks. "
                   "For a sharper photo with the back camera, use "
                   "**Upload a photo** and choose your camera there.")
    with tab_up:
        up = st.file_uploader(
            "Choose a photo", type=["jpg", "jpeg", "png", "webp", "heic", "heif"],
            help="On a phone this also lets you take a new photo with your camera.",
        )

    photo = up or cam
    if photo is None:
        st.info("Works best with one plant in the picture: leaves, stem or "
                "flowers clearly visible.")
    else:
        data = photo.getvalue()
        try:
            preview = plantid.prepare_image(data, max_side=800)
        except Exception:
            st.error("This file could not be opened as a photo. "
                     "Try a JPG or PNG image.")
            st.stop()
        with st.spinner("Checking the photo…"):
            try:
                scores = run_model(data, model_id, api_key)
            except RuntimeError as e:
                st.error(f"Something went wrong: {e} Please try again.")
                st.stop()
        # Verdict first, so it is visible on a phone without scrolling.
        render_result(plantid.make_verdict(scores), preview)

    st.divider()
    st.caption(
        "This is a first check, not a final identification. The model was "
        "trained on about 760 iNaturalist photos from the Netherlands and can "
        "make mistakes, especially with blurry photos, young plants or plants "
        "in winter. When in doubt, do not touch the plant and ask an expert. "
        "Made for HHS AI for Good, Hackathon 7 (SDG 15: Life on Land)."
    )


if __name__ == "__main__":
    main()
