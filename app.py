import streamlit as st
import os
import re
import shutil
from pathlib import Path
import pandas as pd

# =====================================================
# STREAMLIT UI CONFIGURATION
# =====================================================
st.set_page_config(page_title="Short Chapter Scanner", page_icon="🔍", layout="centered")

st.title("🔍 Russian Chapter Word Count & Empty Scan")
st.write("Upload your translated Russian `.txt` chapter files. The app will scan them, count the words, detect empty files or chapters under 200 words, and present a detailed status table.")

# =====================================================
# FILE UPLOADERS
# =====================================================
st.subheader("Upload Chapter Text Files")
uploaded_files = st.file_uploader("Upload `.txt` chapter files", type=["txt"], accept_multiple_files=True)

# =====================================================
# PROCESSING LOGIC
# =====================================================
def extract_file_number(filename):
    match = "".join(c for c in filename if c.isdigit())
    return int(match) if match else 0

def scan_chapters(files):
    input_dir = Path("temp_input")
    
    if input_dir.exists():
        shutil.rmtree(input_dir)
    input_dir.mkdir(exist_ok=True)
    
    # Save uploaded files locally
    for file in files:
        with open(input_dir / file.name, "wb") as f:
            f.write(file.getbuffer())
            
    all_files = [f.name for f in input_dir.iterdir() if f.name.lower().endswith('.txt')]
    
    try:
        sorted_files = sorted(all_files, key=extract_file_number)
    except Exception:
        sorted_files = sorted(all_files)
        
    results = []
    short_files_count = 0
    
    for filename in sorted_files:
        filepath = input_dir / filename
        display_name = filename.replace("never_ending_", "")
        
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                
            words = content.split()
            word_count = len(words)
            
            if word_count == 0:
                status = "EMPTY"
                short_files_count += 1
            elif word_count < 200:
                status = "SHORT (< 200 words)"
                short_files_count += 1
            else:
                status = "OK"
                
            results.append({
                "Chapter File": display_name,
                "Word Count": word_count,
                "Status": status
            })
        except Exception:
            results.append({
                "Chapter File": display_name,
                "Word Count": 0,
                "Status": "FAILED"
            })
            short_files_count += 1
            
    return results, short_files_count

# =====================================================
# MAIN ACTION BUTTON
# =====================================================
if st.button("Scan Chapters"):
    if not uploaded_files:
        st.error("Please upload at least one `.txt` file.")
    else:
        with st.spinner("Scanning chapters..."):
            try:
                data, short_count = scan_chapters(uploaded_files)
                df = pd.DataFrame(data)
                
                st.success(f"Scan complete! Found {short_count} chapters that are empty, short, or failed.")
                
                # Display table
                st.dataframe(df, use_container_width=True)
                
            except Exception as e:
                st.error(f"An error occurred during scanning: {e}")