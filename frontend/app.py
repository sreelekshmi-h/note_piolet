import streamlit as st
import requests


# ============================================================
# Configuration
# ============================================================

BACKEND_URL = "http://127.0.0.1:8000"


# ============================================================
# Page Configuration
# ============================================================

st.set_page_config(
    page_title="AI Notes Assistant",
    page_icon="📚",
    layout="wide"
)


# ============================================================
# Custom CSS (visual polish only — no logic changes)
# ============================================================

st.markdown(
    """
    <style>
    /* Overall page padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1100px;
    }

    /* Title area */
    .app-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 0.25rem;
    }
    .app-header h1 {
        margin-bottom: 0;
        font-size: 2.1rem;
    }
    .app-subtitle {
        color: rgba(120, 120, 130, 0.9);
        font-size: 1.02rem;
        margin-top: 0.15rem;
        margin-bottom: 0.1rem;
    }

    /* Section labels */
    .section-label {
        font-weight: 600;
        font-size: 1.05rem;
        margin-top: 0.5rem;
        margin-bottom: 0.4rem;
    }

    /* Example question buttons */
    div[data-testid="column"] button {
        white-space: normal;
        height: 100%;
        min-height: 3.2rem;
        font-size: 0.85rem;
        border-radius: 10px;
    }

    /* Ask AI primary button */
    button[kind="primary"] {
        border-radius: 10px;
        font-weight: 600;
        height: 3rem;
    }

    /* Answer card */
    .answer-card {
        background-color: rgba(120, 130, 255, 0.06);
        border: 1px solid rgba(120, 130, 255, 0.18);
        border-radius: 12px;
        padding: 1.1rem 1.3rem;
        margin-top: 0.4rem;
    }

    /* Source chip */
    .source-chip {
        display: inline-block;
        background-color: rgba(120, 120, 130, 0.08);
        border: 1px solid rgba(120, 120, 130, 0.18);
        border-radius: 8px;
        padding: 0.35rem 0.7rem;
        margin: 0.2rem 0.35rem 0.2rem 0;
        font-size: 0.88rem;
    }

    /* Sidebar tweaks */
    section[data-testid="stSidebar"] .block-container {
        padding-top: 1.5rem;
    }

    /* Footer caption */
    .footer-caption {
        text-align: center;
        color: rgba(120, 120, 130, 0.8);
        font-size: 0.85rem;
    }

    /* ============================================================
       Mobile / small-screen responsiveness
       ============================================================ */
    @media (max-width: 640px) {

        .block-container {
            padding-top: 1rem;
            padding-left: 1rem;
            padding-right: 1rem;
            padding-bottom: 2rem;
        }

        .app-header h1 {
            font-size: 1.5rem;
        }

        .app-subtitle {
            font-size: 0.92rem;
        }

        .section-label {
            font-size: 0.98rem;
        }

        /* Let the 5 example-question columns wrap into a
           2-per-row (then 1-per-row) grid instead of squeezing
           5 tiny columns into a narrow screen */
        div[data-testid="stHorizontalBlock"] {
            flex-wrap: wrap !important;
            row-gap: 0.5rem;
        }

        div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
            min-width: 45% !important;
            flex: 1 1 45% !important;
        }

        div[data-testid="column"] button {
            font-size: 0.8rem;
            min-height: 3.6rem;
            padding: 0.4rem 0.5rem;
        }

        button[kind="primary"] {
            height: 3.4rem;
            font-size: 1rem;
        }

        .answer-card {
            padding: 0.9rem 1rem;
            font-size: 0.95rem;
        }

        .source-chip {
            font-size: 0.8rem;
            padding: 0.3rem 0.55rem;
        }

        /* Sidebar content a touch tighter on phones */
        section[data-testid="stSidebar"] .block-container {
            padding-top: 1rem;
        }
    }

    @media (max-width: 400px) {
        div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
            min-width: 100% !important;
            flex: 1 1 100% !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# Title
# ============================================================

st.markdown(
    """
    <div class="app-header">
        <h1>📚 AI Notes Assistant</h1>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    '<div class="app-subtitle">Your personal AI study partner powered by your own lecture notes.</div>',
    unsafe_allow_html=True
)

st.write(
    "Upload your lecture notes → ask questions → "
    "get explanations, summaries and MCQs."
)

st.divider()


# ============================================================
# Sidebar
# ============================================================

with st.sidebar:

    st.header("📄 Your Notes")

    st.write(
        "Upload your lecture notes as a PDF."
    )

    uploaded_file = st.file_uploader(
        "Choose a PDF",
        type=["pdf"],
        help="Upload your semester or lecture notes."
    )




    if uploaded_file is not None:

        st.success(
            f"Selected: {uploaded_file.name}"
        )


        # Prevent uploading the same file repeatedly
        if (
            "uploaded_filename" not in st.session_state
            or st.session_state["uploaded_filename"]
            != uploaded_file.name
        ):

            with st.spinner(
                "📚 Processing your notes..."
            ):

                try:

                    files = {
                        "file": (
                            uploaded_file.name,
                            uploaded_file.getvalue(),
                            "application/pdf"
                        )
                    }

                    response = requests.post(
                        f"{BACKEND_URL}/upload",
                        files=files,
                        timeout=120
                    )


                    if response.status_code == 200:

                        data = response.json()

                        st.session_state[
                            "uploaded_filename"
                        ] = uploaded_file.name

                        st.session_state[
                            "uploaded"
                        ] = True

                        st.session_state[
                            "chunks"
                        ] = data["chunks_added"]

                        st.success(
                            "✅ Notes uploaded successfully!"
                        )

                    else:

                        st.error(
                            f"Upload failed: {response.text}"
                        )


                except requests.exceptions.ConnectionError:

                    st.error(
                        "❌ Cannot connect to FastAPI."
                    )

                    st.info(
                        "Start the backend first."
                    )


                except Exception as e:

                    st.error(
                        f"Error: {str(e)}"
                    )



    if st.session_state.get("uploaded"):

        st.divider()

        st.success(
            f"📄 {st.session_state['uploaded_filename']}"
        )

        st.metric(
            label="🧩 Chunks indexed",
            value=st.session_state["chunks"]
        )

    else:
        st.divider()
        st.caption("⬆️ No notes uploaded yet — upload a PDF to get started.")

    st.divider()
    st.caption("Powered by RAG • ChromaDB • Sentence Transformers • Groq")


# ============================================================
# Example Questions
# ============================================================

st.markdown('<div class="section-label">💡 Example Questions</div>', unsafe_allow_html=True)

example_questions = [
    "Explain deadlock in simple words",
    "Give me 5 MCQs from Chapter 3",
    "Summarize the networking module",
    "Explain DMA in simple words",
    "Compare PIO and DMA"
]


cols = st.columns(5)

for i, question in enumerate(example_questions):

    with cols[i]:

        if st.button(
            question,
            use_container_width=True
        ):

            st.session_state["question"] = question


st.markdown('<div class="section-label">💬 Ask a question</div>', unsafe_allow_html=True)

question = st.text_area(
    "💬 Ask something about your notes",
    value=st.session_state.get("question", ""),
    placeholder="Example: Explain DMA in simple words",
    height=100,
    label_visibility="collapsed"
)




if st.button(
    "🤖 Ask AI",
    type="primary",
    use_container_width=True
):

    if not st.session_state.get("uploaded"):

        st.warning(
            "📄 Please upload your lecture notes first."
        )

    elif not question.strip():

        st.warning(
            "💬 Please enter a question."
        )

    else:

        with st.spinner(
            "🔎 Searching your notes and generating an answer..."
        ):

            try:

                response = requests.post(
                    f"{BACKEND_URL}/ask",
                    json={
                        "question": question
                    },
                    timeout=120
                )


                if response.status_code == 200:

                    data = response.json()


                    # ----------------------------------------
                    # Answer
                    # ----------------------------------------

                    st.divider()

                    st.subheader("💬 Answer")

                    st.markdown(
                        f'<div class="answer-card">{data["answer"]}</div>',
                        unsafe_allow_html=True
                    )


                    # ----------------------------------------
                    # Sources
                    # ----------------------------------------

                    sources = data.get(
                        "sources",
                        []
                    )

                    if sources:

                        st.divider()

                        st.subheader(
                            "📖 Sources"
                        )

                        seen = set()
                        chips_html = ""

                        for source in sources:

                            key = (
                                source["source"],
                                source["page"]
                            )

                            if key not in seen:

                                seen.add(key)

                                chips_html += (
                                    '<span class="source-chip">📄 '
                                    f'{source["source"]} — Page '
                                    f'{source["page"]}</span>'
                                )

                        st.markdown(chips_html, unsafe_allow_html=True)


                else:

                    st.error(
                        f"Backend error: {response.text}"
                    )


            except requests.exceptions.ConnectionError:

                st.error(
                    "❌ Could not connect to FastAPI."
                )

                st.code(
                    "python -m uvicorn backend.main:app --reload"
                )


            except requests.exceptions.Timeout:

                st.error(
                    "⏳ The request took too long."
                )


            except Exception as e:

                st.error(
                    f"Something went wrong: {str(e)}"
                )



st.divider()

st.markdown(
    '<div class="footer-caption">RAG • ChromaDB • Sentence Transformers • Groq • FastAPI</div>',
    unsafe_allow_html=True
)