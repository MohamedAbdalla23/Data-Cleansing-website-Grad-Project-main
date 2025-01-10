import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import base64
from io import BytesIO

def handle_duplicates(file, upload_folder):
    filepath = os.path.join(upload_folder, file.filename)
    file.save(filepath)

    df = pd.read_csv(filepath)
    original_df = df.copy()

    duplicate_data = None
    original_rows = df.shape[0]

    duplicate_mask = df.duplicated()
    duplicate_rows = df[duplicate_mask]

    df.drop_duplicates(inplace=True)
    duplicate_rows_count = len(duplicate_rows)
    duplicate_percentage = (duplicate_rows_count / original_rows) * 100

    # Generate the duplicate percentage plot
    fig, ax = plt.subplots()
    labels = ['Duplicate Rows', 'Non-Duplicate Rows']
    sizes = [duplicate_rows_count, original_rows - duplicate_rows_count]
    colors = ['#ff9999','#66b3ff']
    ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')

    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    duplicate_percentage_plot = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close(fig)

    original_df['duplicated'] = duplicate_mask

    duplicate_data = {
        'original_rows': original_rows,
        'duplicate_rows': duplicate_rows_count,
        'duplicate_percentage': round(duplicate_percentage, 2),
        'duplicate_percentage_plot': duplicate_percentage_plot
    }

    original_data = original_df.replace({np.nan: None}).to_dict(orient='records')
    cleaned_data = df.replace({np.nan: None}).to_dict(orient='records')

    return original_data, cleaned_data, duplicate_data
