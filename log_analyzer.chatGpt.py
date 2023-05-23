import streamlit as st
import logging
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
import PyPDF2

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

def main():
    st.title("PDF Text Extractor")
    uploaded_file = st.file_uploader("Upload PDF file", type="pdf")
    
    if uploaded_file is not None:
        pdf_lines = extract_text_from_pdf(uploaded_file)
        
        logger.info("Processing PDF file: %s", uploaded_file.name)
        
        st.subheader("PDF Text Content")
        text_filter = st.text_input("Filter Text")
        
        filtered_lines = [line for line in pdf_lines if text_filter.lower() in line.lower()]
        
        for line in filtered_lines:
            if text_filter:
                line_html = line.replace(
                    text_filter,
                    f'<mark style="background-color: #FFFF00; color: #000000">{text_filter}</mark>'
                )
                st.markdown(line_html, unsafe_allow_html=True)
            else:
                st.text(line)

if __name__ == "__main__":
    main()
