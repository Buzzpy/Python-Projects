import streamlit as st
import pandas as pd
import numpy as np
from pinecone import Pinecone
import os

# Set your Pinecone API key in environment variables
os.environ['PINECONE_API_KEY'] = 'YOUR_API_KEY'

# Initialize Pinecone
pc = Pinecone(api_key=os.environ['PINECONE_API_KEY'])

# Define your index name
index_name = "YOUR_INDEX_NAME"


# Function to fetch data from Pinecone
def fetch_all_data(top_k=1000):
    """
    Fetches `top_k` results from the Pinecone index.
    Returns a pandas DataFrame.
    """
    try:
        # Access Pinecone index
        index = pc.Index(index_name)

        # Query Pinecone for `top_k` results with metadata
        result = index.query(
            vector=np.random.random(1536).tolist(),  # Random vector for testing
            top_k=top_k,
            include_metadata=True
        )

        # Extract metadata from matches and return as DataFrame
        data = [match['metadata'] for match in result['matches']]
        df = pd.DataFrame(data)

        # Clean and preprocess data
        df['SALES'] = pd.to_numeric(df['SALES'], errors='coerce')
        df['QUANTITYORDERED'] = pd.to_numeric(df['QUANTITYORDERED'], errors='coerce')
        df['ORDERDATE'] = pd.to_datetime(df['ORDERDATE'], errors='coerce')
        return df

    except Exception as e:
        st.error(f"Error fetching data from Pinecone: {e}")
        return pd.DataFrame()  # Return an empty DataFrame if an error occurs


# Function to display graphs and analysis
def display_graphs(df):
    """
    Generates and displays graphs from the fetched data.
    """
 

    # Total Sales by Product Line
    if 'PRODUCTLINE' in df.columns and 'SALES' in df.columns:
        product_sales = df.groupby('PRODUCTLINE')['SALES'].sum().sort_values(ascending=False)
        st.write("Total Sales by Product Line:")
        st.bar_chart(product_sales)

    # Quantity Ordered by State
    if 'STATE' in df.columns and 'QUANTITYORDERED' in df.columns:
        state_quantity = df.groupby('STATE')['QUANTITYORDERED'].sum().sort_values(ascending=False)
        st.write("Quantity Ordered by State:")
        st.bar_chart(state_quantity)

    # Sales over Time
    if 'ORDERDATE' in df.columns and 'SALES' in df.columns:
        sales_over_time = df.groupby(df['ORDERDATE'].dt.to_period('M'))['SALES'].sum()
        st.write("Sales Over Time (Monthly):")
        st.line_chart(sales_over_time)


# Streamlit App UI
st.title("Real-Time Sales Data Dashboard")
st.write("This dashboard fetches and visualizes real-time sales data from Pinecone.")

# Fetch data automatically on load
with st.spinner("Fetching data from Pinecone..."):
    df = fetch_all_data(top_k=1000)

# If data is fetched successfully, display graphs
if not df.empty:
    st.success("Data fetched successfully!")
    display_graphs(df)
else:
    st.error("No data fetched. Please check your Pinecone index or API key.")
