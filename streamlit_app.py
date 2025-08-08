"""
Simple Streamlit Dashboard for AI Newsletter Generator 
"""

import streamlit as st
from datetime import datetime
from pathlib import Path

# --- Streamlit config must be first ---
st.set_page_config(page_title="AI Newsletter Generator", layout="wide")

# Force FULL PAGE width for newsletter viewer
st.markdown(
    """
    <style>
    /* Remove ALL container constraints */
    .main .block-container {
        max-width: 100vw !important;
        width: 100vw !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
        padding-top: 1rem !important;
    }
    
    /* Force iframe to use full viewport width */
    div[data-testid='stIFrame'] {
        width: 100vw !important;
        margin-left: calc(-50vw + 50%) !important;
    }
    
    div[data-testid='stIFrame'] > iframe { 
        width: 100vw !important;
        height: 100vh !important;
    }
    
    /* Hide sidebar when viewing newsletter */
    .css-1d391kg { display: none !important; }
    
    /* Remove top padding/margin */
    .stApp > header { display: none !important; }
    
    /* Full width for all elements when viewing */
    div[data-testid='stVerticalBlock'] {
        width: 100vw !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --- Import your config (no extra server needed) ---
try:
    from src.core import config
except ImportError as e:
    st.error(f"Error importing config: {e}")
    st.stop()

OUTPUT_DIR = Path(getattr(config, "OUTPUT_FOLDER", "output")).resolve()

@st.cache_data(ttl=30)
def get_latest_newsletters():
    items = []
    if OUTPUT_DIR.exists():
        for f in OUTPUT_DIR.glob("*.html"):
            try:
                items.append({
                    "filename": f.name,
                    "path": str(f),
                    "date": datetime.fromtimestamp(f.stat().st_mtime),
                    "size": f.stat().st_size
                })
            except OSError:
                pass
    items.sort(key=lambda x: x["date"], reverse=True)
    return items

def generate_newsletter():
    try:
        from src.newsletter_generator.scraper import get_all_articles
        from src.newsletter_generator.simple_categorized_summarizer import run_categorized_summarization
        import tempfile
        import json

        p = st.progress(0); msg = st.empty()
        msg.text("Scraping articles..."); p.progress(20)
        articles = get_all_articles()
        
        # Save articles to a temporary file for the summarizer
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as temp_file:
            json.dump({"articles": articles}, temp_file, ensure_ascii=False, indent=2)
            temp_filepath = temp_file.name
        
        msg.text("Analyzing and categorizing..."); p.progress(60)
        result = run_categorized_summarization(temp_filepath)
        
        # Clean up temporary file
        import os
        os.unlink(temp_filepath)
        
        msg.text("Newsletter generated successfully."); p.progress(100)
        return True, result
    except Exception as e:
        return False, str(e)

def main():
    # Session state (store HTML + title for viewing)
    st.session_state.setdefault("view_html", None)
    st.session_state.setdefault("view_title", None)

    st.markdown("# AI Newsletter Generator")
    st.caption(f"Output folder: {OUTPUT_DIR}")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Generate New Newsletter")
        if st.button("Generate Newsletter", type="primary", use_container_width=True):
            with st.spinner("Generating..."):
                ok, res = generate_newsletter()
                if ok:
                    st.success("Done.")
                    get_latest_newsletters.clear()
                    st.rerun()
                else:
                    st.error(f"Error: {res}")

    with col2:
        st.subheader("Recent Newsletters")
        if st.button("Refresh", use_container_width=True):
            get_latest_newsletters.clear()
            st.rerun()

        for i, n in enumerate(get_latest_newsletters()[:10]):
            with st.container():
                st.markdown(f"**{n['filename']}**")
                st.caption(f"Created: {n['date'].strftime('%Y-%m-%d %H:%M:%S')} • Size: {n['size']//1024} KB")

                c1, c2 = st.columns(2)
                with c1:
                    if st.button("View", key=f"view_{i}", use_container_width=True):
                        try:
                            html = Path(n["path"]).read_text(encoding="utf-8")
                            st.session_state.view_html = html
                            st.session_state.view_title = n["filename"]
                            st.rerun()
                        except Exception as e:
                            st.error(f"Could not open file: {e}")

                with c2:
                    try:
                        with open(n["path"], "rb") as f:
                            st.download_button(
                                "Download",
                                data=f.read(),
                                file_name=n["filename"],
                                mime="text/html",
                                key=f"dl_{i}",
                                use_container_width=True
                            )
                    except FileNotFoundError:
                        st.button("Unavailable", disabled=True, key=f"disabled_{i}")

                st.divider()

    # ---- FULL PAGE Viewer ----
    if st.session_state.get("view_html"):
        # Create a minimal header that spans full width
        st.markdown("---")
        
        # Compact header with close button
        col1, col2 = st.columns([8, 1])
        with col1:
            st.markdown(f"**{st.session_state.get('view_title', '')}**")
        with col2:
            if st.button("✕", help="Close", use_container_width=True):
                st.session_state.view_html = None
                st.session_state.view_title = None
                st.rerun()

        # FULL VIEWPORT newsletter viewer
        st.components.v1.html(
            st.session_state["view_html"], 
            height=800,  # Use viewport height
            scrolling=True,
            width=None  # Let it use full available width
        )





    # ---- Stats ----
    st.markdown("---")
    items = get_latest_newsletters()
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("Total Newsletters", len(items))
    with c2:
        if items: st.metric("Latest", items[0]["date"].strftime("%m/%d"))
    with c3:
        if items: st.metric("Total Size", f"{sum(i['size'] for i in items)//1024} KB")

if __name__ == "__main__":
    main()
