from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory,send_file,session
import csv
import os
import pandas as pd
import numpy as np
from missing_value import handle_missing_values
from outliers import handle_outliers
from duplicates import handle_duplicates
from invalid_format import handle_invalid_format
from werkzeug.utils import secure_filename
import matplotlib.pyplot as plt
from io import BytesIO
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import json


import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import base64
import io
import dash_table
import plotly.express as px


# Initialize Flask app
flask_app = Flask(__name__)
# flask_app.secret_key = '1345'  # Replace with a real secret key

UPLOAD_FOLDER = 'uploads'
CLEANED_FOLDER = 'cleaned'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CLEANED_FOLDER, exist_ok=True)

flask_app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
flask_app.config['CLEANED_FOLDER'] = CLEANED_FOLDER
flask_app.config['ALLOWED_EXTENSIONS'] = {'csv'}
cleaned_data = []


# Initialize Dash app
dash_app = dash.Dash(__name__, server=flask_app, url_base_pathname='/dash/', external_stylesheets=[dbc.themes.BOOTSTRAP])

# Define the layout of the Dash app
dash_app.layout = dbc.Container([
    
    dbc.Row([
        dbc.Col(html.H1("Upload and Visualize CSV"), className="text-center mb-4")
    ]),
    dbc.Row([
        dbc.Col(dcc.Upload(
            id='upload-data',
            children=html.Div(['Drag and Drop or ', html.A('Select Files')]),
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
            multiple=False  # Single file upload
        ), width=12)
    ]),
    dbc.Row([
        dbc.Col([
            html.Div(id='uploaded-csv')
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id='column-dropdown',
                options=[],  # Initially empty, will be populated by callback
                placeholder='Select a column',
                style={'width': '100%'}
            )
        ], width=6),
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='scatter-plot')
        ], width=6),
        dbc.Col([
            dcc.Graph(id='line-plot')
        ], width=6)
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='bar-plot')
        ], width=6),
        dbc.Col([
            dcc.Graph(id='histogram')
        ], width=6)
    ])
])

# Function to detect outliers using IQR method
def detect_outliers(df, column):
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    outliers = (df[column] < lower_bound) | (df[column] > upper_bound)
    return outliers

# Callback to update column dropdown options based on uploaded CSV file
@dash_app.callback(
    Output('column-dropdown', 'options'),
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename')]
)
def update_column_dropdown(contents, filename):
    options = []
    if contents is not None:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        try:
            if 'csv' in filename:
                # Assume that the user uploaded a CSV file
                df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
                options = [{'label': col, 'value': col} for col in df.columns]
        except Exception as e:
            print(e)
    return options

# Callback to display uploaded CSV data
@dash_app.callback(
    Output('uploaded-csv', 'children'),
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename')]
)
def update_uploaded_csv(contents, filename):
    table = html.Div()
    if contents is not None:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        try:
            if 'csv' in filename:
                # Assume that the user uploaded a CSV file
                df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))

                if 'is_outlier' not in df.columns:
                    df['is_outlier'] = False  # Initialize outlier column

                # Detect outliers
                for col in df.select_dtypes(include=np.number):
                    outliers = detect_outliers(df, col)
                    df.loc[outliers, 'is_outlier'] = True

                # Convert DataFrame to HTML table
                table = dash_table.DataTable(
                    id='table',
                    columns=[{"name": i, "id": i} for i in df.columns],
                    data=df.to_dict('records'),
                    style_data_conditional=[
                        {
                            'if': {'filter_query': '{is_outlier} eq true'},
                            'backgroundColor': 'rgba(255, 0, 0, 0.3)'  # Highlight outliers in red
                        }
                    ],
                    style_table={'overflowX': 'scroll'},
                    style_cell={'minWidth': '180px', 'width': '180px', 'maxWidth': '180px'},
                )

        except Exception as e:
            print(e)
    return table

# Callback to update plots based on column selection
@dash_app.callback(
    [Output('scatter-plot', 'figure'),
     Output('line-plot', 'figure'),
     Output('bar-plot', 'figure'),
     Output('histogram', 'figure')],
    [Input('column-dropdown', 'value')],
    [State('upload-data', 'contents'),
     State('upload-data', 'filename')]
)
def update_output(selected_column, contents, filename):
    scatter_fig = {}
    line_fig = {}
    bar_fig = {}
    hist_fig = {}

    if contents is not None:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        try:
            if 'csv' in filename:
                # Assume that the user uploaded a CSV file
                df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))

                if selected_column and selected_column in df.columns:
                    # Detect outliers
                    outliers = detect_outliers(df, selected_column)
                    df['is_outlier'] = np.where(outliers, 'Outlier', 'Normal')

                    # Scatter Plot
                    scatter_fig = px.scatter(df, x=df.index, y=df[selected_column], color='is_outlier',
                                             color_discrete_map={'Outlier': 'red', 'Normal': 'blue'},
                                             title=f'Scatter Plot ({selected_column})')

                    # Line Plot
                    line_fig = px.line(df, x=df.index, y=df[selected_column], color='is_outlier',
                                       color_discrete_map={'Outlier': 'red', 'Normal': 'blue'},
                                       title=f'Line Plot ({selected_column})')

                    # Bar Plot
                    bar_fig = px.bar(df, x=df.index, y=df[selected_column], color='is_outlier',
                                     color_discrete_map={'Outlier': 'red', 'Normal': 'blue'},
                                     title=f'Bar Plot ({selected_column})')

                    # Histogram
                    hist_fig = px.histogram(df, x=df[selected_column], color='is_outlier',
                                            color_discrete_map={'Outlier': 'red', 'Normal': 'blue'},
                                            title=f'Histogram ({selected_column})')

        except Exception as e:
            print(e)

    return scatter_fig, line_fig, bar_fig, hist_fig


# Flask Routes
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in flask_app.config['ALLOWED_EXTENSIONS']

def clean_data(df, method='mean'):
    cleaned_df = df.copy()
    for column in cleaned_df.columns:
        if pd.api.types.is_numeric_dtype(cleaned_df[column]):
            if method == 'mean':
                cleaned_df[column].fillna(cleaned_df[column].mean(), inplace=True)
            elif method == 'median':
                cleaned_df[column].fillna(cleaned_df[column].median(), inplace=True)
            elif method == 'mode':
                cleaned_df[column].fillna(cleaned_df[column].mode()[0], inplace=True)
            elif method == 'zero':
                cleaned_df[column].fillna(0, inplace=True)
        else:
            if method == 'mode':
                cleaned_df[column].fillna(cleaned_df[column].mode()[0], inplace=True)
            else:
                cleaned_df[column].fillna('Random-Value', inplace=True)
                
    return cleaned_df

def calculate_missing_percentage(df):
    total_cells = df.size
    missing_cells = df.isnull().sum().sum()
    missing_percentage = (missing_cells / total_cells) * 100
    return missing_percentage

def plot_missing_values_pie(df):
    missing_values = df.isnull().mean() * 100
    labels = missing_values.index
    sizes = missing_values.values
    colors = plt.get_cmap('tab20')(range(len(labels)))  # Get colors for each label
    explode = [0.1] * len(labels)  # explode all slices slightly

    plt.figure(figsize=(8, 6))
    plt.pie(sizes, explode=explode, autopct='%1.1f%%', shadow=True, startangle=140, colors=colors)
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.title('Percentage of Missing Values per Column')
    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    encoded_image = base64.b64encode(image_png).decode('utf-8')

    column_details = [{'label': label, 'color': mcolors.to_hex(color)} for label,color in zip(labels,colors)]

    return encoded_image, column_details

@flask_app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify(error="No file part"), 400
    
    file = request.files['file']
    method = request.form.get('method', 'mean')  # Default method if not provided
    if file.filename == '':
        return jsonify(error="No selected file"), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(flask_app.config['UPLOAD_FOLDER'], filename)
        
        try:
            file.save(file_path)
            df = pd.read_csv(file_path)

            original_data = df.replace({np.nan: None}).to_dict(orient='records')
            cleaned_df = clean_data(df, method)
            cleaned_data = cleaned_df.replace({np.nan: None}).to_dict(orient='records')

            missing_percentage = calculate_missing_percentage(df)
            missing_plot, column_details = plot_missing_values_pie(df)

            # Save cleaned_df to CSV
            cleaned_filename = f"cleaned_{filename}"
            cleaned_filepath = os.path.join(flask_app.config['CLEANED_FOLDER'], cleaned_filename)
            cleaned_df.to_csv(cleaned_filepath, index=False)

            cleaned_data = cleaned_df.replace({np.nan: None}).to_dict(orient='records')


            return jsonify({
              'original': original_data, 
              'cleaned': cleaned_data, 
              'filename': cleaned_filename, 
              'missing_percentage': missing_percentage,
              'missing_plot': missing_plot,
              'column_details': column_details
                              
              }), 200
        
        except Exception as e:
            return jsonify(error=f"Error processing file: {e}"), 500
    
    else:
        return jsonify(error="Invalid file format"), 400

# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'csv'}

# def clean_data(df, method):
#     if method == 'mean':
#         return df.fillna(df.mean(numeric_only=True))
#     elif method == 'median':
#         return df.fillna(df.median(numeric_only=True))
#     elif method == 'mode':
#         return df.fillna(df.mode().iloc[0])
#     else:
#         return df.fillna(method)

@flask_app.route('/missing_values', methods=['GET', 'POST'])
def missing_values():
    if request.method == 'POST':
        file = request.files['csv_file']
        method = request.form['method']
        if file.filename == '':
            return 'No selected file'
        if file:
            original_data, cleaned_data, missing_percentage, missing_plot = handle_missing_values(file, method, UPLOAD_FOLDER)
            return render_template('missing_values.html', original_data=original_data, cleaned_data=cleaned_data, missing_percentage=missing_percentage, missing_plot=missing_plot)
    return render_template('missing_values.html')

@flask_app.route('/outliers', methods=['GET', 'POST'])
def outliers():
    if request.method == 'POST':
        file = request.files['file']
        if file.filename == '':
            return 'No selected file'
        if file:
            try:
                filename = secure_filename(file.filename)
                original_table, outliers_table, cleaned_table, outlier_count, total_count, outliers_percentage_plot, cleaned_file, error = handle_outliers(file, flask_app.config['UPLOAD_FOLDER'], flask_app.config['CLEANED_FOLDER'], filename)
                if error:
                    return f"Error processing file: {error}"
                return render_template('outliers.html', 
                                       original_table=original_table, 
                                       outliers_table=outliers_table, 
                                       cleaned_table=cleaned_table,
                                       outlier_count=outlier_count,
                                       total_count=total_count,
                                       outliers_percentage_plot=outliers_percentage_plot,
                                       cleaned_file=cleaned_file)
            except ValueError as e:
                return f"Error processing file: {e}"

    return render_template('outliers.html')

@flask_app.route('/save_changes', methods=['POST'])
def save_changes():
    data = request.json.get('data')
    filename = request.args.get('filename')

    if not data or not filename:
        return jsonify({'message': 'Invalid data or filename'}), 400

    cleaned_filepath = os.path.join(flask_app.config['CLEANED_FOLDER'], filename)

    try:
        # Convert the data to DataFrame
        df = pd.DataFrame(data)
        
        # Ensure correct headers are used and handle missing values
        # Remove any fully empty rows that might have been added inadvertently
        df = df.dropna(how='all')
        
        # Save DataFrame to CSV without an extra index column
        df.to_csv(cleaned_filepath, index=False, header=True, na_rep='')

        return jsonify({'message': 'Changes saved successfully'}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@flask_app.route('/download/<filename>', methods=['GET'])
def download_cleaned_file(filename):
    return send_from_directory(flask_app.config['CLEANED_FOLDER'], filename, as_attachment=True)

@flask_app.route('/duplicates', methods=['GET', 'POST'])
def duplicates():
    if request.method == 'POST':
        file = request.files['csv_file']
        if file.filename == '':
            return 'No selected file'
        if file:
            original_data, cleaned_data, duplicate_data = handle_duplicates(file, UPLOAD_FOLDER)
            return render_template('duplicates.html', original_data=original_data, cleaned_data=cleaned_data, duplicate_data=duplicate_data)
    return render_template('duplicates.html')





@flask_app.route('/invalid_format', methods=['GET', 'POST'])
def invalid_format():
    global cleaned_data
    if request.method == 'POST':
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            fieldnames, original_data, cleaned_data_tmp, invalid_count, total_count, plot_url = handle_invalid_format(file, UPLOAD_FOLDER)
            cleaned_data = cleaned_data_tmp
            return render_template('invalid_format.html', fieldnames=fieldnames, original_data=original_data, cleaned_data=cleaned_data, invalid_count=invalid_count, total_count=total_count, plot_url=plot_url)
    return render_template('invalid_format.html')

@flask_app.route('/save_cleaned_data', methods=['POST'])
def save_cleaned_data():
    global cleaned_data
    try:
        cleaned_data = request.json
        return jsonify({"status": "success", "message": "Data saved successfully!"})
    except Exception as e:
        print(e)
        return jsonify({"status": "error", "message": "Failed to save data."}), 500




@flask_app.route('/download_cleaned_data', methods=['GET'])
def download_cleaned_data():
    global cleaned_data
    if not cleaned_data:
        return jsonify({"status": "error", "message": "No cleaned data found."}), 404

    # Create a CSV file in memory
    output = io.StringIO()
    fieldnames = cleaned_data[0].keys() if cleaned_data else []
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(cleaned_data)
    output.seek(0)

    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name='cleaned_data.csv'
    )



@flask_app.route('/dashboard')
def index():
    return render_template('dashboard.html')

@flask_app.route('/')
def auth():
    return render_template('Auth.html')

@flask_app.route('/home')
def home():
    return render_template('home.html')

@flask_app.route('/About')
def about():
    return render_template('About.html')




if __name__ == '__main__':
    flask_app.run(debug=True, port=2025)
