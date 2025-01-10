import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import io
import base64

def handle_missing_values(file, method, upload_folder):
    filepath = os.path.join(upload_folder, file.filename)
    file.save(filepath)

    df = pd.read_csv(filepath)
    original_df = df.copy()

    missing_percentage = df.isnull().mean().mean() * 100

    for column in df.columns:
        if df[column].isnull().any():
            if pd.api.types.is_numeric_dtype(df[column]):
                if method == 'mean':
                    df[column].fillna(df[column].mean(), inplace=True)
                elif method == 'median':
                    df[column].fillna(df[column].median(), inplace=True)
                elif method == 'mode':
                    df[column].fillna(df[column].mode()[0], inplace=True)
                elif method == 'zero':
                    df[column].fillna(0, inplace=True)
            else:
                if method == 'mode':
                    df[column].fillna(df[column].mode()[0], inplace=True)
                else:
                    df[column].fillna('RandomValue', inplace=True)

    original_data = original_df.replace({np.nan: None}).to_dict(orient='records')
    cleaned_data = df.replace({np.nan: None}).to_dict(orient='records')

    # Generate missing values chart
    plt.figure(figsize=(6, 4))
    plt.barh(df.columns, df.isnull().mean() * 100)
    plt.xlabel('Percentage of Missing Values')
    plt.ylabel('Columns')
    plt.title('Missing Values Percentage per Column')
    plt.tight_layout()

    # Convert plot to PNG image
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    missing_values_plot = base64.b64encode(img.getvalue()).decode('utf8')
    plt.close()

    return original_data, cleaned_data, missing_percentage, missing_values_plot
