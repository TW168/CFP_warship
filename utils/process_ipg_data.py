import re
import pandas as pd 
import sqlite3
import os

def process_ipg_data(file_path):
    """
    Process data from ipg and perform necessary transformations.

    Parameters:
    - file_path (str): Path to the Excel file.

    Returns:
    - pd.DataFrame: Processed DataFrame with selected columns.
    """

    conn = sqlite3.connect('ipg.db')
    # Read the Excel file into a DataFrame
    df = pd.read_excel(file_path)
    # Use os.path.basename to get the file name from the file path
    file_name = os.path.basename(file_path)
    # Filter out rows with 'Product Code' equal to 'SUBTOTAL'
    df = df[df['Product Code'] != 'SUBTOTAL']
  
    # Get the name of the last column
    last_column_name = df.columns[-1]
    df['report_run'] = last_column_name

    # Define a regex pattern to extract date and hour
    pattern = re.compile(r'(\d{4}-\d{1,2}-\d{1,2})\s*H(\d{1,2})M\d+')

    # Use regex to extract date and hour for each row in the 'report_run' column
    df['extracted'] = df['report_run'].apply(lambda x: pattern.search(str(x)))

    # Extracted date and hour
    df['extracted_date'] = df['extracted'].apply(lambda x: x.group(1) if x else None)
    df['extracted_hour'] = df['extracted'].apply(lambda x: x.group(2) if x else None)

    # Convert 'extracted_hour' to int
    df['report_hour'] = pd.to_numeric(df['extracted_hour'], errors='coerce').astype('Int64')

    # Convert 'extracted_date' to datetime
    df['report_date'] = pd.to_datetime(df['extracted_date'], errors='coerce')

    # Convert date columns to datetime
    date_columns = ['Truck Appointment Date (YY/MM/DD)', 'PickUp Date (YY/MM/DD)',
                    'Require Date (YY/MM/DD)', 'Schedule Date (YY/MM/DD)',
                    'Change Date (YY/MM/DD)']

    for col in date_columns:
        df[col.replace(' (YY/MM/DD)', '')] = pd.to_datetime(df[col], format='%y/%m/%d', errors='coerce')

    # Columns to keep
    columns_to_keep = [
        'SITE', 'B/L Number', 'B/L Weight (LB)', 'Freight Amount ($)', 'Truck Appt. Time',
        'State', 'Ship to City', 'Ship to Customer',
        'Order Number', 'Order Item', 'CSR', 'Freight Term',
        'Unshipped Weight (Lb)', 'Product Code', 'Pick Weight (Lb)',
        'Number of Pallet', 'Pickup By', 'Carrier ID',
        'Arrange By', 'Unit Freight (cent/Lb)', 'Waybill Number', 'Sales Code',
        'Transportation Code', 'Transaction Type', 'Product Group',
        'report_run', 'report_hour', 'report_date', 'Truck Appointment Date',
        'PickUp Date', 'Require Date', 'Schedule Date', 'Change Date'
    ]

    # Select the columns to keep
    df = df[columns_to_keep]
    # Add file name to df
    df['file_name'] = file_name
        
    query = 'Select City, State, Latitude, Longitude from lat_lng'
    lat_lng_df = pd.read_sql_query(query, conn)

    # Merge the lat_lng data with your original DataFrame
    df = pd.merge(df, lat_lng_df, left_on=['State', 'Ship to City'], right_on=['State', 'City'], how='left')
   
    # Check for existing records with the same file_name
    # existing_query = f"SELECT DISTINCT file_name FROM shipments WHERE file_name = '{file_name}'"
    
    # existing_records = pd.read_sql_query(existing_query, conn)
    # # print(existing_records)
    # # Filter out existing records
    # new_records_df = df[~df['file_name'].isin(existing_records['file_name'])]

    # Insert new records into the shipments table
    df.to_sql('shipments', conn, index=False, if_exists='append')
    conn.close()
    return df