from swift.common.db import get_db_connection

import subprocess

def get_dbs():
    command = [
        'find', '/', '-type', 'f',
        '(', '-name', '*.sqlite', '-o', '-name', '*.db', '-o', '-name', '*.sqlite3', ')'
    ]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        print()
    return stdout.splitlines()

# # Iterate over each line in the output
# for line in stdout.splitlines():
#     if "containers" in line:
#         c = ContainerBroker(line)
#         d = c.get_info()
#         print(d["bytes_used"])


# print()
import pathlib

#root = pathlib.Path("/home")
#a = list(root.rglob("*containers*.db"))

def generate_named_bucket_query(bucket_dict):
    """
    Generate an SQL query to count the number of objects in each named bucket range.

    Parameters:
    - bucket_dict (dict): Dictionary where the key is the bucket name and the value is the upper bound of the bucket range.

    Returns:
    - str: The SQL query string.
    """
    # Initialize the start size for the first bucket
    start = 0

    # Create CASE statements and ORDER BY statements
    case_statements = []
    order_statements = []

    # Iterate through the dictionary to create CASE statements
    for i, (name, upper_bound) in enumerate(bucket_dict.items()):
        # Handle the bucket range with the previous start and the current upper bound
        case_statements.append(f"WHEN size BETWEEN {start} AND {upper_bound} THEN '{name}'")
        order_statements.append(f"WHEN Bucket = '{name}' THEN {i + 1}")
        # Update start for the next bucket range
        start = upper_bound + 1

    # Add an 'else' case for any sizes larger than the largest bucket
    case_statements.append(f"ELSE 'Above {upper_bound}'")

    # Join CASE statements to form the complete CASE block
    case_block = "CASE " + " ".join(case_statements) + " END"

    # Generate the complete SQL query
    query = f"""
SELECT
    {case_block} AS Bucket,
    COUNT(*) AS NumberOfObjects
FROM object
GROUP BY Bucket
ORDER BY
    CASE { ' '.join(order_statements) } ELSE {len(bucket_dict) + 1} END;
"""
    return query

# Example usage:
bucket_dict = {
    '0-1 KB': 1024,
    '0-10 KB': 10240,
    '10-100 KB': 102400,
    '100 KB - 1 MB': 1048576,
    '1 MB - 10 MB': 10485760,
    '10 MB - 25 MB': 26214400,
    '25 MB - 50 MB': 52428800,
    '50 MB - 100 MB': 104857600,
    '100 MB - 500 MB': 524288000,
    '500 MB - 1 GB': 1073741824,
    '1 GB - 5 GB': 5368709120
}



import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect("/home/asudakov/go/src/github.com/AlinaSecret/swiftacular/containers.db", check_same_thread=False)

# Execute the SQL query

sql_query = generate_named_bucket_query(bucket_dict)
count = "SELECT COUNT(*) AS TotalNumberOfObjects FROM object;"
# Execute the query and fetch the results
res = conn.execute(sql_query)
rows = res.fetchall()
print(" ".join(map(lambda a: f"{a[0]}={a[1]}", rows)))