import streamlit as st
import pandas as pd
import google.generativeai as genai
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest

# Configure the API key securely from Streamlit's secrets
# Make sure to add GOOGLE_API_KEY in secrets.toml (for local) or Streamlit Cloud Secrets
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Streamlit App UI
st.title("Fraudulent Company Detection using Anomaly Detection")
st.write("Upload a financial statement (CSV) to scan for anomalies or fraudulent patterns.")

# File uploader for CSV file
uploaded_file = st.file_uploader("Choose a CSV file with financial data", type="csv")

# Function to load and preprocess the financial data
def load_and_preprocess_data(uploaded_file):
    try:
        # Load the CSV file into a DataFrame
        df = pd.read_csv(uploaded_file)
        
        # Basic check on data
        st.write("Loaded Data:")
        st.write(df.head())  # Display the first few rows of the dataframe
        
        # Preprocessing: Assume numerical columns are the ones to analyze for anomaly
        numeric_df = df.select_dtypes(include=[np.number])
        
        # Standardize the data for anomaly detection
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(numeric_df)
        
        return scaled_data, df
    except Exception as e:
        st.error(f"Error in data loading or preprocessing: {e}")
        return None, None

# Function to detect anomalies using Isolation Forest
def detect_anomalies(data):
    try:
        # Using Isolation Forest for anomaly detection
        model = IsolationForest(contamination=0.05)  # Set contamination to 5%
        predictions = model.fit_predict(data)
        
        # Convert predictions to a DataFrame with 'Anomaly' column
        return predictions
    except Exception as e:
        st.error(f"Error in anomaly detection: {e}")
        return None

# Function to generate explanation using Generative AI
def generate_explanation(anomalies, df):
    try:
        # Check if any anomalies were detected
        if anomalies is not None and len(anomalies) > 0:
            # Find indices of anomalous rows
            anomaly_indices = np.where(anomalies == -1)[0]
            anomaly_rows = df.iloc[anomaly_indices]
            
            # Create a prompt to generate an explanation
            prompt = f"The following financial data is flagged as anomalous or potentially fraudulent:\n{anomaly_rows}\nPlease provide an explanation for these anomalies."
            
            # Generate a response from the AI model
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            st.write("Generated Explanation:")
            st.write(response.text)
        else:
            st.write("No anomalies detected.")
    except Exception as e:
        st.error(f"Error generating explanation: {e}")

# Process the uploaded file and detect anomalies
if uploaded_file is not None:
    # Load and preprocess the data
    scaled_data, df = load_and_preprocess_data(uploaded_file)
    
    if scaled_data is not None:
        # Detect anomalies in the dataset
        anomalies = detect_anomalies(scaled_data)
        
        # Display the results
        if anomalies is not None:
            # Add the anomaly results as a column in the original dataframe
            df['Anomaly'] = anomalies
            st.write("Anomaly Detection Results:")
            st.write(df)
            
            # Generate explanation for the anomalies
            generate_explanation(anomalies, df)
