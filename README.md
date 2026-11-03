# NGO Resource & Volunteer Management System (Streamlit)

## Run locally
```bash
python -m venv .venv
.venv\\Scripts\\activate   # Windows
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Deploy on Streamlit Community Cloud
1. Push this folder to a GitHub repository.
2. In https://share.streamlit.io click **Create app**.
3. Select your repository and branch.
4. Set **Main file path** to `streamlit_app.py`.
5. Click **Deploy**.

SQLite database is created automatically. Note: Streamlit Community Cloud's local filesystem may reset; for durable production data, connect a hosted database.
