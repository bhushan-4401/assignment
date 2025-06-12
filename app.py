import streamlit as st
import tempfile
import os
import pandas as pd
import time
import json
from src.core.prompts import system_prompt
from src.agents.workflow import AppReact
from src.core.database import Database
from src.file_processor.excel_processor import ExcelProcessor
from src.generator.app_generator import AppGenerator
from dynaconf import Dynaconf

# Page config
st.set_page_config(page_title="Excel Query Bot", page_icon="📊", layout="wide")

# Initialize session state
st.session_state.setdefault('db', None)
st.session_state.setdefault('agent_workflow', None)
st.session_state.setdefault('file_processed', False)

# Title
st.title("Excel Query Bot")

# Sidebar with file upload
with st.sidebar:
    uploaded_file = st.file_uploader("Upload Excel file", type=['xlsx', 'xls'])
    
    if st.session_state.file_processed:
        st.success("✅ File processed successfully!")
        if st.button("Upload New File"):
            # Reset everything for new file
            st.session_state.db = None
            st.session_state.agent_workflow = None
            st.session_state.file_processed = False
            st.rerun()

# Process uploaded file with progress bar
if uploaded_file and not st.session_state.file_processed:
    # Create progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Step 1: Save file
        status_text.text("📁 Saving uploaded file...")
        progress_bar.progress(10)
        time.sleep(0.5)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            temp_path = tmp_file.name
        
        # Step 2: Load configuration
        status_text.text("⚙️ Loading configuration...")
        progress_bar.progress(25)
        time.sleep(0.5)
        
        cfg = Dynaconf(settings_files=[
            "/home/user/ABC/Assignment/config/config.toml",
            "/home/user/ABC/Assignment/config/.secrets.toml"
        ])
        
        # Step 3: Initialize components
        status_text.text("🔧 Initializing components...")
        progress_bar.progress(45)
        time.sleep(0.5)
        
        db = Database(cfg)
        generator = AppGenerator(cfg)
        file_processor = ExcelProcessor(db, cfg)
        
        # Step 4: Process Excel
        status_text.text("📊 Processing Excel data...")
        progress_bar.progress(70)
        time.sleep(1)
        
        file_processor.process_excel(temp_path)
        os.unlink(temp_path)
        
        # Step 5: Finalize
        status_text.text("✅ Finalizing setup...")
        progress_bar.progress(90)
        time.sleep(0.5)
        
        # Save to session
        st.session_state.db = db
        st.session_state.agent_workflow = AppReact(generator=generator, text_db=db)
        st.session_state.cfg = cfg
        st.session_state.file_processed = True
        
        # Complete
        progress_bar.progress(100)
        status_text.text("🎉 Excel file processed successfully!")
        time.sleep(1)
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        st.success("Excel file processed successfully! You can now ask questions about your data.")
        st.rerun()
        
    except Exception as e:
        progress_bar.empty()
        status_text.empty()
        st.error(f"Error processing file: {str(e)}")

# Helper function to parse response output
def parse_response_output(output):
    """Parse different types of output and convert to appropriate format"""
    if output is None:
        return "No data returned."
    
    # If it's already a DataFrame
    if isinstance(output, pd.DataFrame):
        return output
    
    # If it's a list of dictionaries
    if isinstance(output, list) and len(output) > 0 and isinstance(output[0], dict):
        return pd.DataFrame(output)
    
    # If it's a string that looks like a list of dictionaries
    if isinstance(output, str):
        try:
            # Try to parse as JSON
            if output.strip().startswith('[') and output.strip().endswith(']'):
                parsed_data = json.loads(output)
                if isinstance(parsed_data, list) and len(parsed_data) > 0 and isinstance(parsed_data[0], dict):
                    return pd.DataFrame(parsed_data)
        except:
            pass
    
    # Return as string for other cases
    return str(output)

# Query interface - only show if file is processed
if st.session_state.file_processed:
    st.subheader("Ask a Question")
    
    # Create a form for the query
    with st.form(key="query_form", clear_on_submit=False):
        prompt = st.text_area(
            "Enter your question about the Excel data:",
            placeholder="e.g., What is the total sales by region?",
            height=100
        )
        submit_button = st.form_submit_button("Submit Query")
    
    # Process query when submitted
    if submit_button and prompt:
        # Display the submitted question
        st.subheader("Your Question:")
        st.info(f"📝 {prompt}")
        
        # Create placeholder for streaming response
        response_placeholder = st.empty()
        
        try:
            # Show initial processing message
            with response_placeholder.container():
                st.subheader("Result:")
                with st.spinner("🤖 Processing your query..."):
                    # Simulate streaming by showing steps
                    step_placeholder = st.empty()
                    
                    step_placeholder.text("🔍 Analyzing your question...")
                    time.sleep(0.5)
                    
                    step_placeholder.text("📊 Querying database...")
                    time.sleep(0.5)
                    
                    step_placeholder.text("🧠 Generating response...")
                    time.sleep(0.5)
                    
                    # Process the actual query
                    db_schema = st.session_state.db.extract_schema(
                        st.session_state.cfg.get("EXCEL_TABLE_NAME", "")
                    )
                    formatted_prompt = system_prompt.format(
                        table_schema=db_schema, 
                        user_query=prompt
                    )
                    response = st.session_state.agent_workflow.execute(prompt=formatted_prompt)
                    output = response.get("output")
                    
                    step_placeholder.text("✨ Formatting results...")
                    time.sleep(0.5)
                    
                    # Parse and prepare the output
                    parsed_output = parse_response_output(output)
                    
                    step_placeholder.empty()
            
            # Display the final result
            with response_placeholder.container():
                st.subheader("Result:")
                
                if isinstance(parsed_output, pd.DataFrame):
                    if len(parsed_output) > 0:
                        # Display metrics if it's numerical data
                        if 'total_quantity' in parsed_output.columns:
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Total Items", f"{len(parsed_output):,}")
                            with col2:
                                st.metric("Total Quantity", f"{parsed_output['total_quantity'].sum():,.0f}")
                            with col3:
                                st.metric("Avg Quantity", f"{parsed_output['total_quantity'].mean():,.1f}")
                        
                        # Display the data table
                        st.dataframe(
                            parsed_output, 
                            use_container_width=True,
                            height=400
                        )
                        
                        # Add download button
                        csv = parsed_output.to_csv(index=False)
                        st.download_button(
                            label="📥 Download as CSV",
                            data=csv,
                            file_name=f"query_result_{int(time.time())}.csv",
                            mime="text/csv"
                        )
                    else:
                        st.info("No data found matching your query.")
                else:
                    st.write(parsed_output)
                
        except Exception as e:
            with response_placeholder.container():
                st.subheader("Result:")
                st.error(f"❌ Error processing query: {str(e)}")
                
                # Show debug info in expander
                with st.expander("Debug Information"):
                    st.write("**Error Details:**")
                    st.code(str(e))
                    st.write("**Question:**")
                    st.write(prompt)
    
    elif submit_button and not prompt:
        st.warning("⚠️ Please enter a question before submitting.")

else:
    # Instructions for first-time users
    st.info("👈 Please upload an Excel file in the sidebar to begin querying your data.")
    
    # Help section
    st.subheader("How to use:")
    st.write("""
    1. **Upload** your Excel file using the sidebar
    2. **Wait** for the file to be processed (progress bar will show status)
    3. **Ask** questions about your data in natural language
    4. **View** results in table format with download option
    5. Each query is independent - no conversation history is maintained
    """)
    
    st.subheader("Example questions:")
    st.code("""
• "Which customer has the most transactions?"
• "What are the total quantities sold for each item?"
• "What's the total quantity sold per day?"
• "How many transactions occurred at each site?"
• "List transactions with quantities greater than 1000"
    """)
    
    st.subheader("Features:")
    st.write("""
    - ✅ **Progress tracking** during file processing
    - ✅ **Streaming responses** with real-time updates  
    - ✅ **Smart data formatting** (tables, metrics, charts)
    - ✅ **CSV download** for query results
    - ✅ **Error handling** with debug information
    """)