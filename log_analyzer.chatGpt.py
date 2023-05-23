import streamlit as st
import logging
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
import PyPDF2
import time
import json

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

def process_log(log_data, text_filter):
    tracer = trace.get_tracer_provider().get_tracer(__name__)
    with tracer.start_as_current_span("Log Processing"):
        time.sleep(1)  # Simulating processing time
        filtered_lines = [line.replace(text_filter, f"<span style='font-size:300%; color:green'>{text_filter}</span>") for line in log_data if text_filter.lower() in line.lower()]
        return filtered_lines

def write_to_log_file(log_entry):
    log_file_path = 'logs/app_log.txt'
    
    with open(log_file_path, 'a') as file:
        file.write(json.dumps(log_entry) + '\n')

def main():
    st.title("PDF Text Extractor and Log Analyzer")
    
    with trace.get_tracer_provider().get_tracer(__name__).start_as_current_span("App Execution"):
        upload_start_time = time.time()
        
        uploaded_file = st.file_uploader("Upload PDF file", type="pdf")
        
        if uploaded_file is not None:
            pdf_lines = parse_pdf(uploaded_file)
            
            logger.info("Processing PDF file: %s", uploaded_file.name)
            
            st.subheader("PDF Text Content")
            text_filter = st.text_input("Filter Text")
            
            filtered_lines = process_log(pdf_lines, text_filter)
            
            for line in filtered_lines:
                st.markdown(line, unsafe_allow_html=True)
            
            upload_end_time = time.time()
            latency = upload_end_time - upload_start_time
            logger.info("PDF upload and rendering latency: %.2f seconds", latency)

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
