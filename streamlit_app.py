import streamlit as st
import pandas as pd
import google.generativeai as genai
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest

# Configure the API key securely from Streamlit's secrets
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Streamlit App UI
st.title("Anomaly Detection for Fraudulent Companies")
st.write("Upload a financial statement to check for potential anomalies based on patterns of fraudulent companies.")

# File uploader for the financial statement (CSV or Excel)
uploaded_file = st.file_uploader("Choose a financial statement file (CSV/Excel)", type=["csv", "xlsx"])

if uploaded_file is not None:
    # Load the file into a DataFrame based on its type
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.write("Financial Statement Data:")
    st.dataframe(df.head())  # Show the first few rows of the data

    # Extract relevant features from the financial statement
    # This step assumes that the columns are standardized (you would typically clean and prepare the data before this)
    numeric_columns = df.select_dtypes(include=["float64", "int64"]).columns.tolist()

    # If no numeric columns, display an error
    if not numeric_columns:
        st.error("No numeric columns found in the file. Anomaly detection requires numeric data.")
    else:
        # Standardize the data (important for anomaly detection algorithms)
        scaler = StandardScaler()
        data_scaled = scaler.fit_transform(df[numeric_columns])

        # Apply Isolation Forest (anomaly detection model)
        model = IsolationForest(contamination=0.1)  # contamination: expected fraction of outliers
        model.fit(data_scaled)
        
        # Predict anomalies (-1 for anomalies, 1 for normal)
        predictions = model.predict(data_scaled)
        df['Anomaly'] = predictions

        # Display results
        st.write("Anomaly Detection Results:")
        st.dataframe(df[['Anomaly'] + numeric_columns].head())

        # Display the number of anomalies found
        num_anomalies = (df['Anomaly'] == -1).sum()
        st.write(f"Number of anomalies detected: {num_anomalies}")

# Optionally, you can also add generative AI-based analysis:
prompt = st.text_input("Optional: Ask AI for insights on financial patterns", "")
if st.button("Generate AI Insights"):
    try:
        # Generate insights based on the prompt entered by the user
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        st.write("AI Insights:")
        st.write(response.text)
    except Exception as e:
        st.error(f"Error generating AI insights: {e}")
