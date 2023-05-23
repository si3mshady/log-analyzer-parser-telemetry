import streamlit as st
import logging
import json
import re
import PyPDF2
import time

# Configure logging
logger = logging.getLogger("app")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('noSpoon.log')
formatter = logging.Formatter(
    '{"@timestamp": "%(asctime)s", "message": "%(message)s", "log.level": "%(levelname)s"}'
)
handler.setFormatter(formatter)
logger.addHandler(handler)

def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    lines = []
    for page in pdf_reader.pages:
        lines.extend(page.extract_text().split('\n'))
    return lines

def parse_pdf(file):
    time.sleep(2)  # Simulating parsing time
    return extract_text_from_pdf(file)

def parse_json(file):
    time.sleep(1)  # Simulating parsing time
    return json.load(file)

def process_log(log_data, text_filter):
    filtered_lines = [
        re.sub(
            f"({re.escape(text_filter)})",
            r"<span style='background-color: green; font-weight: bold; font-size: 130%;'>\1</span>",
            line,
            flags=re.IGNORECASE
        )
        for line in log_data
        if re.search(re.escape(text_filter), line, flags=re.IGNORECASE)
    ]
    return filtered_lines

def write_to_log_file(log_entry):
    with open('noSpoon.log', 'a') as file:
        file.write(json.dumps(log_entry) + '\n')

def main():
    st.title("File Text Extractor and Log Analyzer")
    
    upload_start_time = time.time()
    
    file_type = st.selectbox("Select File Type", ("json", "txt", "pdf"), index=2)
    
    if file_type:
        uploaded_file = st.file_uploader("Upload File", type=file_type)
        
        if uploaded_file is not None:
            if file_type == "pdf":
                file_lines = parse_pdf(uploaded_file)
            elif file_type == "json":
                file_lines = parse_json(uploaded_file)
            else:
                file_lines = uploaded_file.readlines()
            
            logger.info("Processing %s file: %s", file_type.upper(), uploaded_file.name)
            
            st.subheader("File Text Content")
            text_filter = st.text_input("Filter Text")
            
            filtered_lines = process_log(file_lines, text_filter)
            
            for line in filtered_lines:
                st.markdown(line, unsafe_allow_html=True)

            upload_end_time = time.time()
            latency = upload_end_time - upload_start_time
            logger.info("%s upload and rendering latency: %.2f seconds", file_type.upper(), latency)

            time_to_visible = time.time() - upload_end_time
            logger.info("Time to display output on screen: %.2f seconds", time_to_visible)

            log_entry_upload = {
                "@timestamp": int(upload_start_time * 1000),
                "message": f"{file_type.upper()} upload and rendering latency: {latency:.2f} seconds",
                "log.level": "INFO"
            }
            log_entry_visible = {
                "@timestamp": int(upload_end_time * 1000),
                "message": f"Time to display output on screen: {time_to_visible:.2f} seconds",
                "log.level": "INFO"
            }

            write_to_log_file(log_entry_upload)
            write_to_log_file(log_entry_visible)

if __name__ == "__main__":
    main()
