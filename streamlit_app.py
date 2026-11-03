import streamlit as st
import sqlite3
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="NGO Resource Management", page_icon="🤝", layout="wide")
DB_PATH = Path(__file__).parent / "ngo.db"

TABLES = {
    "Donors": ["Name", "Phone", "Email", "Donation", "Date"],
    "Beneficiaries": ["Name", "Age", "Phone", "Address", "Requirement"],
    "Resources": ["Resource", "Category", "Quantity", "Condition", "Location"],
    "Volunteers": ["Name", "Phone", "Email", "Skills", "Availability"],
    "Interns": ["Name", "College", "Department", "Start Date", "End Date"],
    "Events": ["Event Name", "Date", "Location", "Coordinator", "Description"],
}

def connect():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    with connect() as conn:
        for table, fields in TABLES.items():
            cols = ", ".join(f'"{f}" TEXT' for f in fields)
            conn.execute(f'CREATE TABLE IF NOT EXISTS "{table}" (id INTEGER PRIMARY KEY AUTOINCREMENT, {cols})')
init_db()

st.sidebar.title("🤝 Umiya Social Trust")
page = st.sidebar.radio("Navigation", ["Dashboard", *TABLES.keys(), "Reports"])
st.sidebar.caption("Digital NGO Resource & Volunteer Management")
st.title("🤝 NGO Resource & Volunteer Management")
st.caption("A simple digital platform to manage trust activities and records.")

if page == "Dashboard":
    st.subheader("Dashboard Overview")
    cols = st.columns(len(TABLES))
    with connect() as conn:
        for col, (table, fields) in zip(cols, TABLES.items()):
            count = conn.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
            col.metric(table, count)
    st.info("Use the sidebar to add, view, and manage records in each module.")
    st.subheader("Recent Records")
    with connect() as conn:
        for table in TABLES:
            df = pd.read_sql_query(f'SELECT * FROM "{table}" ORDER BY id DESC LIMIT 5', conn)
            if not df.empty:
                st.markdown(f"**{table}**")
                st.dataframe(df, use_container_width=True, hide_index=True)

elif page in TABLES:
    fields = TABLES[page]
    st.subheader(f"{page} Management")
    with st.expander(f"➕ Add {page[:-1] if page.endswith('s') else page} record", expanded=True):
        with st.form(f"add_{page}"):
            values = {}
            for field in fields:
                values[field] = st.text_input(field)
            submitted = st.form_submit_button("Save Record", type="primary")
        if submitted:
            if not any(v.strip() for v in values.values()):
                st.warning("Please enter at least one field.")
            else:
                placeholders = ",".join("?" for _ in fields)
                cols = ",".join(f'"{f}"' for f in fields)
                with connect() as conn:
                    conn.execute(f'INSERT INTO "{page}" ({cols}) VALUES ({placeholders})', tuple(values[f] for f in fields))
                st.success("Record added successfully!")
                st.rerun()
    with connect() as conn:
        df = pd.read_sql_query(f'SELECT * FROM "{page}" ORDER BY id DESC', conn)
    search = st.text_input("🔎 Search records", key=f"search_{page}")
    if search and not df.empty:
        mask = df.astype(str).apply(lambda col: col.str.contains(search, case=False, na=False)).any(axis=1)
        df = df[mask]
    st.dataframe(df, use_container_width=True, hide_index=True)
    if not df.empty:
        ids = df["id"].tolist()
        delete_id = st.selectbox("Select ID to delete", ids, key=f"del_{page}")
        if st.button("🗑️ Delete selected record", key=f"delete_btn_{page}"):
            with connect() as conn:
                conn.execute(f'DELETE FROM "{page}" WHERE id=?', (int(delete_id),))
            st.success("Record deleted.")
            st.rerun()

elif page == "Reports":
    st.subheader("📊 Reports")
    with connect() as conn:
        for table in TABLES:
            df = pd.read_sql_query(f'SELECT * FROM "{table}"', conn)
            st.markdown(f"**{table} ({len(df)} records)**")
            if not df.empty:
                st.download_button(f"Download {table} CSV", df.to_csv(index=False).encode("utf-8"), f"{table.lower()}_report.csv", "text/csv", key=f"download_{table}")
            else:
                st.caption("No records yet.")
