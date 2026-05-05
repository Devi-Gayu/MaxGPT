# --------------------------- Imports ---------------------------
from sqlalchemy import create_engine, MetaData, Table, select, text
from sqlalchemy.orm import sessionmaker
import matplotlib.pyplot as plt
import pandas as pd
import os
import groq
import shutil
import json
from datetime import datetime

# --------------------------- Configuration ---------------------------

# ⚠️ Replace with your actual credentials safely
DATABASE_URL = "mysql+pymysql://<username>:<password>@127.0.0.1/production_chatbot"
GROQ_API_KEY = "your_groq_api_key_here"

# Create DB engine
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
Session = sessionmaker(bind=engine)
session = Session()

# Initialize Groq client
client = groq.Groq(api_key=GROQ_API_KEY)

# Create folders
os.makedirs("results", exist_ok=True)
os.makedirs("graphs", exist_ok=True)

# --------------------------- Helper Functions ---------------------------

def execute_query(query):
    """Execute SQL query and return dataframe"""
    try:
        df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        print("Error executing query:", e)
        return None


def save_results(df):
    """Save results to CSV"""
    filename = f"./results/results_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
    df.to_csv(filename, index=False)
    print(f"Results saved as: {filename}")
    return filename


def generate_graph(df):
    """Generate basic graphs"""
    try:
        for col in df.select_dtypes(include=['int64', 'float64']).columns:
            
            # Histogram
            plt.figure()
            df[col].hist()
            plt.title(f'Histogram of {col}')
            plt.savefig(f'./graphs/histogram_{col}.png')
            plt.close()

            # Pie Chart (for limited unique values)
            if df[col].nunique() <= 10:
                plt.figure()
                df[col].value_counts().plot.pie(autopct='%1.1f%%')
                plt.title(f'Pie Chart of {col}')
                plt.savefig(f'./graphs/pie_{col}.png')
                plt.close()

    except Exception as e:
        print("Graph generation error:", e)


def log_query(query):
    """Log user queries"""
    log_data = {
        "query": query,
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    with open("query_log.json", "a") as f:
        f.write(json.dumps(log_data) + "\n")

    print("Query logged successfully.")


def ask_groq(prompt):
    """Send prompt to Groq LLM"""
    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        print("Groq error:", e)
        return None


# --------------------------- Main Flow ---------------------------

def main():
    print("=== Production Data Chatbot ===")

    user_query = input("Enter your query: ")

    # Convert NL to SQL (via Groq)
    sql_query = ask_groq(f"Convert this to SQL: {user_query}")
    print("\nGenerated SQL:", sql_query)

    # Execute query
    df = execute_query(sql_query)

    if df is not None and not df.empty:
        print("\nQuery Results:")
        print(df.head())

        # Save results
        save_results(df)

        # Generate graphs
        generate_graph(df)

        # Log query
        log_query(user_query)

    else:
        print("No results found.")


# --------------------------- Run ---------------------------
if __name__ == "__main__":
    main()
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

Session = sessionmaker(bind=engine)
session = Session()

# Initialize Groq client
client = groq.Groq(api_key=GROQ_API_KEY)

# --------------------------- Main Execution ---------------------------

def execute_query(query):
    try:
        result = session.execute(text(query))
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
        return df
    except Exception as e:
        print("Error executing query:", e)
        return None


def save_results(df):
    try:
        filename = f'./results/results_{pd.Timestamp.now().strftime("%Y%m%d%H%M%S")}.csv'
        df.to_csv(filename, index=False)
        print(f"Results saved as: {filename}")
    except Exception as e:
        print("Error saving results:", e)


def generate_graphs(df):
    try:
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns

        for col in numeric_cols:
            # Histogram
            plt.figure()
            df[col].hist()
            plt.title(f'Histogram of {col}')
            plt.savefig(f'./graphs/histogram_{col}.png')
            plt.close()

            # Pie chart
            if df[col].nunique() <= 10:
                plt.figure()
                df[col].value_counts().plot.pie(autopct='%1.1f%%')
                plt.title(f'Pie Chart of {col}')
                plt.savefig(f'./graphs/pie_{col}.png')
                plt.close()

    except Exception as e:
        print("Error generating graphs:", e)


def log_query(query):
    try:
        log_entry = {
            "query": query,
            "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        with open("query_log.json", "a") as f:
            f.write(json.dumps(log_entry) + "\n")

        print("Query logged successfully.")
    except Exception as e:
        print("Error logging query:", e)


def get_sql_from_groq(user_input):
    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "user", "content": f"Convert the following into SQL query: {user_input}"}
            ]
        )

        sql_query = response.choices[0].message.content
        return sql_query

    except Exception as e:
        print("Error from Groq:", e)
        return None


# --------------------------- Run Program ---------------------------

if __name__ == "__main__":
    
    # Create folders if not exist
    os.makedirs("results", exist_ok=True)
    os.makedirs("graphs", exist_ok=True)

    user_input = input("Enter your query: ")

    sql_query = get_sql_from_groq(user_input)

    if sql_query:
        print("Generated SQL Query:", sql_query)

        df = execute_query(sql_query)

        if df is not None and not df.empty:
            print(df.head())

            save_results(df)
            generate_graphs(df)
            log_query(user_input)

        else:
            print("No data returned.")
    else:
        print("Failed to generate SQL query.")
