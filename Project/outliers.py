import pandas as pd
import os
import matplotlib.pyplot as plt
import io
import base64
from bs4 import BeautifulSoup
from werkzeug.utils import secure_filename



def detect_outliers(df):
    outlier_counts = 0
    outliers_mask = pd.DataFrame(False, index=df.index, columns=df.columns)  # Initialize a mask with False values
    
    for col in df.select_dtypes(include='number').columns:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        mask = (df[col] < lower_bound) | (df[col] > upper_bound)
        outliers_mask[col] = mask
        outlier_counts += mask.sum()
    
    return outliers_mask, outlier_counts

def df_to_html_with_outliers(df, outliers_mask):
    df_html = df.copy()
    for col in df.select_dtypes(include='number').columns:
        df_html[col] = df_html.apply(
            lambda row: f'<span class="outlier">{row[col]}</span>' if outliers_mask.at[row.name, col] else row[col], axis=1)
    return df_html.to_html(classes='table table-striped', escape=False)

def df_to_html_editable(df):
    html = df.to_html(classes='table table-striped', header=True, index=False, escape=False)
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table')
    for row in table.find_all('tr'):
        delete_button = soup.new_tag('button', **{'class': 'delete-row btn btn-danger'})
        delete_button.string = 'Delete'
        td = soup.new_tag('td')
        td.append(delete_button)
        row.append(td)
        for cell in row.find_all('td'):
            cell['class'] = cell.get('class', []) + ['edit-cell']
    return str(soup)

def clean_outliers(df):
    cleaned_df = df.copy()  # Make a copy to avoid modifying the original DataFrame
    for col in df.select_dtypes(include='number').columns:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        cleaned_df[col] = df[col].apply(lambda x: upper_bound if x > upper_bound else (lower_bound if x < lower_bound else x))
    return cleaned_df

def plot_outliers_percentage(outlier_count, total_count):
    percentages = [outlier_count / total_count * 100, (total_count - outlier_count) / total_count * 100]
    labels = ['Outliers', 'Non-Outliers']
    fig, ax = plt.subplots()
    ax.pie(percentages, labels=labels, autopct='%1.1f%%', colors=['red', 'green'])
    ax.axis('equal')

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()

    return plot_url

def handle_outliers(file, upload_folder, cleaned_folder, filename):
    filepath = os.path.join(upload_folder, filename)
    file.save(filepath)

    try:
        df = pd.read_csv(filepath)
        print(f"DataFrame loaded successfully with shape: {df.shape}")
    except Exception as e:
        return None, None, None, None, None, None, None, f"Error reading CSV file: {e}"

    try:
        original_table = df.to_html(classes='table table-striped', header=True, index=False)

        outliers_mask, outlier_count = detect_outliers(df)

        outliers_table = df_to_html_with_outliers(df, outliers_mask)

        cleaned_df = clean_outliers(df)

        cleaned_table = df_to_html_editable(cleaned_df)

        cleaned_filepath = os.path.join(cleaned_folder, filename)
        cleaned_df.to_csv(cleaned_filepath, index=False, header=True, na_rep='')  # Ensure index is not saved as column

        total_count = len(df)
        outliers_percentage_plot = plot_outliers_percentage(outlier_count, total_count)

        return original_table, outliers_table, cleaned_table, outlier_count, total_count, outliers_percentage_plot, filename, None
    except Exception as e:
        return None, None, None, None, None, None, None, f"Error processing outliers: {e}"
