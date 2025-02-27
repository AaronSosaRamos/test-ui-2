import os
import streamlit as st
import requests
import json

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

def call_api(endpoint, payload):
    url = f"{os.environ.get('ENDPOINT_URL')}{endpoint}"
    response = requests.post(url, json=payload)
    return response.json() if response.status_code == 200 else {"error": "Failed to fetch data"}

def main():
    st.set_page_config(page_title="AI Pipeline Request Handler", layout="wide")
    st.title("📊 AI Pipeline Request Handler")
    
    file_urls = st.text_area("File URLs (comma-separated)")
    file_types = st.text_area("File Types (comma-separated)")
    query = st.text_area("Optional Query")
    output_desc = st.text_area("Optional Output Description")
    
    if st.button("🚀 Start Processing"):
        file_urls_list = [url.strip() for url in file_urls.split(",") if url.strip()]
        file_types_list = [ft.strip() for ft in file_types.split(",") if ft.strip()]
        
        payload = {
            "file_urls": file_urls_list,
            "file_types": file_types_list,
            "query": query,
            "output_desc": output_desc,
            "previous_agentic_results": {}  # Initialize an empty dictionary for accumulation
        }
        
        accumulated_results = {}  # Store all previous results progressively
        
        steps = [
            ("Step 1: Generating Functional & Technical Requirements Analysis", "/api/discovery-multi-agent/ftr-analyst"),
            ("Step 2: Generating AS-IS Process Document", "/api/discovery-multi-agent/aip-documenter"),
            ("Step 3: Updating TO-BE Data Flow", "/api/discovery-multi-agent/tbd-updater"),
            ("Step 4: Generating Data Gap Analysis & Solutions", "/api/discovery-multi-agent/das-generator"),
            ("Step 5: Generating TO-BE Process Document", "/api/discovery-multi-agent/tbpd-generator"),
            ("Step 6: Generating Access Setup & Support Requirements Plan", "/api/discovery-multi-agent/assr-planifier"),
            ("Step 7: Generating Updated Timeline", "/api/discovery-multi-agent/ut-generator")
        ]
        
        for step_name, endpoint in steps:
            st.subheader(step_name)
            
            # Update payload with all accumulated results
            payload["previous_agentic_results"] = accumulated_results.copy()
            
            # Call the API
            result = call_api(endpoint, payload)
            st.json(result)
            
            # Merge result into accumulated_results
            accumulated_results.update(result)
        
        # Step 8: Generate HTML Report
        st.subheader("Step 8: Generating HTML Report")
        html_payload = {"json_content": accumulated_results}
        html_results = call_api("/api/discovery-multi-agent/html-generator", html_payload)
        st.json(html_results)
        
        # Step 9: Generate PDF Report
        st.subheader("Step 9: Generating PDF Report")
        pdf_payload = {"html_content": html_results}
        pdf_response = requests.post(f"{os.environ.get('ENDPOINT_URL')}/api/discovery-multi-agent/pdf-generator", json=pdf_payload, stream=True)
        
        if pdf_response.status_code == 200:
            st.success("✅ PDF Generated Successfully!")
            st.download_button(label="📥 Download PDF", data=pdf_response.content, file_name="discovery_result.pdf", mime="application/pdf")
        else:
            st.error("❌ Failed to generate PDF")

if __name__ == "__main__":
    main()
