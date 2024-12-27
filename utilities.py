import pandas as pd
from datetime import datetime
import streamlit as st

def calculate_monthly_expenses(csv_file, percentage_table):
    """
    Calculate total expenses per user per month based on user percentages.

    Args:
        csv_file (str): Path to the CSV file containing expenses.
        percentage_table (list of dict): List of dictionaries with user_id and percentage.

    Returns:
        pd.DataFrame: A DataFrame with columns: user_id, year_month, total_expense.
    """
    # Load expenses CSV into a DataFrame
    expenses = pd.read_csv(csv_file)

    # Convert date column to datetime and create year_month column
    expenses['date'] = pd.to_datetime(expenses['date'])
    expenses['year_month'] = expenses['date'].dt.to_period('M')

    # Create a DataFrame from the percentage table
    percentages = pd.DataFrame(percentage_table)

    # Normalize percentages to ensure they sum to 100
    percentages['percentage'] = percentages['percentage'] / percentages['percentage'].sum()

    # Group expenses by year_month and calculate total per month
    monthly_totals = expenses.groupby('year_month')['total_amount'].sum().reset_index()

    # Expand the data to include user contributions
    user_expenses = []
    for _, row in monthly_totals.iterrows():
        for _, user in percentages.iterrows():
            user_expenses.append({
                'user_id': user['user_id'],
                'year_month': row['year_month'],
                'total_expense': row['total_amount'] * user['percentage']
            })

    # Convert user_expenses into a DataFrame
    user_expenses_df = pd.DataFrame(user_expenses)

    return user_expenses_df

# Streamlit UI
if __name__ == "__main__":
    st.title("Monthly Expense Calculator")

    st.header("Upload CSV File")
    csv_file = st.file_uploader("Upload your expenses CSV file", type=["csv"])

    st.header("User Percentage Table")
    percentage_input = st.text_area(
        "Enter user percentages as JSON (e.g., [{\"user_id\": \"user_1\", \"percentage\": 50}, ...])",
        "[{\"user_id\": \"user_1\", \"percentage\": 50}, {\"user_id\": \"user_2\", \"percentage\": 30}, {\"user_id\": \"user_3\", \"percentage\": 20}]"
    )

    if csv_file and percentage_input:
        try:
            # Load percentages from user input
            percentage_table = eval(percentage_input)

            # Process the CSV file
            result = calculate_monthly_expenses(csv_file, percentage_table)

            # Display the result
            st.header("Result")
            st.dataframe(result)

            # Option to download the result as CSV
            csv = result.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download result as CSV",
                data=csv,
                file_name="user_expenses.csv",
                mime="text/csv",
            )
        except Exception as e:
            st.error(f"An error occurred: {e}")
