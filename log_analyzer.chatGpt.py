import streamlit as st
import logging
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
import PyPDF2
import time
import json
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

trace.set_tracer_provider(TracerProvider())
span_processor = BatchSpanProcessor(OTLPSpanExporter())
trace.get_tracer_provider().add_span_processor(span_processor)

def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    lines = []
    for page in pdf_reader.pages:
        lines.extend(page.extract_text().split('\n'))
    return lines

def parse_pdf(file):
    tracer = trace.get_tracer_provider().get_tracer(__name__)
    with tracer.start_as_current_span("PDF Parsing"):
        time.sleep(2)  # Simulating parsing time
        return extract_text_from_pdf(file)

def parse_json(file):
    tracer = trace.get_tracer_provider().get_tracer(__name__)
    with tracer.start_as_current_span("JSON Parsing"):
        time.sleep(1)  # Simulating parsing time
        return json.load(file)

def process_log(log_data, text_filter):
    tracer = trace.get_tracer_provider().get_tracer(__name__)
    with tracer.start_as_current_span("Log Processing"):
        time.sleep(1)  # Simulating processing time
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
    log_file_path = 'app_log.json'
    
    with open(log_file_path, 'a') as file:
        file.write(json.dumps(log_entry) + '\n')

def main():
    st.title("File Text Extractor and Log Analyzer")
    
    with trace.get_tracer_provider().get_tracer(__name__).start_as_current_span("App Execution"):
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
                    "start_time": upload_start_time,
                    "end_time": upload_end_time,
                    "elapsed_time": latency
                }
                log_entry_visible = {
                    "start_time": upload_end_time,
                    "end_time": time.time(),
                    "elapsed_time": time_to_visible
                }

                write_to_log_file(log_entry_upload)
                write_to_log_file(log_entry_visible)

if __name__ == "__main__":
    main()
