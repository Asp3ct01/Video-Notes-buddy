import streamlit as st
import time
from test import VideoNotesBot
import threading
from queue import Queue
from queue import Empty

# Initialize session state
if 'bot' not in st.session_state:
    st.session_state.bot = VideoNotesBot()
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'summary' not in st.session_state:
    st.session_state.summary = ""
if 'progress_value' not in st.session_state:
    st.session_state.progress_value = 0

def process_video(url, model, progress_queue):
    try:
        # Change model if needed
        if model:
            st.session_state.bot.change_model(model)
        
        # Process the video
        summary = st.session_state.bot.process_video(url)
        progress_queue.put(("complete", summary))
    except Exception as e:
        progress_queue.put(("error", str(e)))

def main():
    st.set_page_config(
        page_title="Video Notes Buddy",
        page_icon="📝",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS for better styling
    st.markdown("""
        <style>
        .stApp {
            max-width: 1200px;
            margin: 0 auto;
        }
        .main .block-container {
            padding-top: 2rem;
        }
        .stTextInput > div > div > input {
            background-color: #f0f2f6;
        }
        .stSelectbox > div > div > select {
            background-color: #f0f2f6;
        }
        </style>
    """, unsafe_allow_html=True)

    # Header
    st.title("🎥 Video Notes Buddy")
    st.markdown("### Your Smart Study Companion")

    # Create two columns for input and output
    col1, col2 = st.columns([1, 1])

    with col1:
        # Input section
        st.subheader("Input")
        url = st.text_input("YouTube URL", placeholder="Enter YouTube video URL here...")
        
        # Model selection
        model = st.selectbox(
            "Select Model",
            options=list(st.session_state.bot.available_models.keys()),
            index=0
        )

        # Generate button
        if st.button("Generate Summary", type="primary", disabled=st.session_state.processing):
            if not url:
                st.error("Please enter a valid YouTube URL")
            else:
                st.session_state.processing = True
                st.session_state.summary = ""
                st.session_state.progress_value = 0
                
                # Create a queue for progress updates
                progress_queue = Queue()
                
                # Start processing in a separate thread
                thread = threading.Thread(
                    target=process_video,
                    args=(url, model, progress_queue),
                    daemon=True
                )
                thread.start()
                
                # Create a placeholder for the progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Monitor progress
                while st.session_state.processing:
                    try:
                        status, result = progress_queue.get_nowait()
                        if status == "complete":
                            st.session_state.summary = result
                            st.session_state.processing = False
                            break
                        elif status == "error":
                            st.error(f"Error: {result}")
                            st.session_state.processing = False
                            break
                    except Empty:
                        # Update progress bar
                        st.session_state.progress_value = min(90, st.session_state.progress_value + 1)
                        progress_bar.progress(st.session_state.progress_value)
                        status_text.text("Processing video...")
                        time.sleep(0.1)
                
                progress_bar.progress(100)
                status_text.text("Complete!")

    with col2:
        # Output section
        st.subheader("Summary")
        if st.session_state.summary:
            st.markdown(st.session_state.summary)
        else:
            st.info("Your summary will appear here after processing.")

    # Footer
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center'>
            <p>Made with ❤️ for better learning</p>
            <p>Process YouTube videos and get instant summaries</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 