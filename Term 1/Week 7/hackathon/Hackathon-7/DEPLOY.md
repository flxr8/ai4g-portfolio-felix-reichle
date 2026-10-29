# Putting the app online (Streamlit Community Cloud, free)

1. Put this folder in a **public or private GitHub repo**. Do **not** upload `.streamlit/secrets.toml` (it is in `.gitignore`).
2. Go to https://share.streamlit.io and sign in with GitHub.
3. Click **Create app** → pick your repo → main file: `app.py` → **Deploy**.
4. Open the app's **Settings → Secrets** and paste:
   ```
   ROBOFLOW_API_KEY = "your-private-api-key"
   ROBOFLOW_MODEL_ID = "your-project-slug/3"
   ```
5. Save. The app restarts and you get a link like `https://your-app.streamlit.app`. Open it on your phone.

**Camera on a phone:** the camera only works over https, which Streamlit Cloud provides. "Take a photo" uses the browser camera; "Upload a photo" lets the phone use its normal camera app, which usually gives a sharper photo with the back camera.

**Where to find the model ID:** in Roboflow open your project → *Deploy* (or the model page). The ID is `project-slug/version-number`, for example `netherlands-plant-field-id-5/3`.
