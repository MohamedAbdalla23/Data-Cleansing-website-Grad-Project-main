// Wrap your JavaScript code inside the DOMContentLoaded event listener to ensure it runs after the document is fully loaded
document.addEventListener('DOMContentLoaded', function() {

    // Function to handle form submission and file upload
    document.getElementById('uploadForm').addEventListener('submit', function(e) {
        e.preventDefault();

        let csvFile = document.getElementById('csvFile').files[0];
        if (!csvFile) {
            alert('Please select a file.');
            return;
        }

        let method = document.getElementById('method').value;
        let formData = new FormData();
        formData.append('file', csvFile);
        formData.append('method', method);

        fetch('/upload', {
            method: 'POST',
            body: formData
        }).then(response => {
            if (!response.ok) {
                return response.json().then(errorData => {
                    throw new Error(errorData.error);
                });
            }
            return response.json();
        }).then(data => {
            // Display the original and cleaned tables, and missing stats
            displayTable('originalTableContainer', data.original);
            displayCleanedTable(data.cleaned);
            displayMissingStats(data.missing_percentage, data.column_details, data.missing_plot);

            // Enable download button
            let downloadCsvBtn = document.getElementById('downloadCsvBtn');
            if (downloadCsvBtn) { // Check if button exists
                downloadCsvBtn.addEventListener('click', function() {
                    downloadCsv(data.cleaned, data.filename); // Function to trigger download
                });
            } else {
                console.error('Download button not found.'); // Log an error if button not found
            }

        }).catch(error => {
            console.error('Error:', error.message);
            alert('Error: ' + error.message);
        });
    });

    // Function to download CSV file
    function downloadCsv(data, filename) {
        let csvContent = 'data:text/csv;charset=utf-8,';
        csvContent += Object.keys(data[0]).join(',') + '\n';
        data.forEach(row => {
            csvContent += Object.values(row).join(',') + '\n';
        });

        // Create a hidden link element and trigger download
        let encodedUri = encodeURI(csvContent);
        let link = document.createElement('a');
        link.setAttribute('href', encodedUri);
        link.setAttribute('download', filename);
        document.body.appendChild(link); // Append link to the body (required for Firefox)
        link.click(); // Programmatically click the link to trigger download
        document.body.removeChild(link); // Clean up by removing the link from the DOM
    }

});

function displayMissingStats(missingPercentage, columnDetails, missingPlot) {
    document.getElementById('missingPercentage').textContent = missingPercentage.toFixed(2) + '%';
    
    let columnDetailsContainer = document.getElementById('columnDetails');
    columnDetailsContainer.innerHTML = '';

    columnDetails.forEach(detail => {
        let listItem = document.createElement('li');
        listItem.className = 'list-group-item';
        listItem.style.backgroundColor = detail.color;
        listItem.style.color = getContrastingColor(detail.color); // Ensure text is readable
        listItem.textContent = `${detail.label}`;
        columnDetailsContainer.appendChild(listItem);
    });

    let img = document.getElementById('missingPlot');
    img.src = `data:image/png;base64,${missingPlot}`;
}

// Helper function to get a contrasting color (white or black) for the text
function getContrastingColor(hex) {
    // Remove the hash at the start if it's there
    hex = hex.replace('#', '');

    // Convert to RGB values
    var r = parseInt(hex.substr(0, 2), 16);
    var g = parseInt(hex.substr(2, 2), 16);
    var b = parseInt(hex.substr(4, 2), 16);

    // Calculate the contrast color
    var contrast = (r * 0.299 + g * 0.587 + b * 0.114) > 186 ? '#000000' : '#FFFFFF';
    return contrast;
}

function displayTable(containerId, data) {
    let tableContainer = document.getElementById(containerId);
    tableContainer.innerHTML = '';

    if (data.length === 0) {
        tableContainer.textContent = 'No data available.';
        return;
    }

    let table = document.createElement('table');
    table.className = 'table table-bordered'; // Bootstrap classes for better styling

    let headerRow = document.createElement('tr');
    Object.keys(data[0]).forEach(key => {
        let th = document.createElement('th');
        th.textContent = key;
        headerRow.appendChild(th);
    });
    table.appendChild(headerRow);

    data.forEach(row => {
        let tr = document.createElement('tr');
        Object.values(row).forEach(value => {
            let td = document.createElement('td');
            td.textContent = value !== null ? value : '';
            tr.appendChild(td);
        });
        table.appendChild(tr);
    });

    tableContainer.appendChild(table);
}


function displayCleanedTable(data) {
    let table = document.createElement('table');
    table.className = 'table table-bordered table-striped'; // Bootstrap classes for better styling

    // Create table header
    let headerRow = document.createElement('tr');
    Object.keys(data[0]).forEach(key => {
        let th = document.createElement('th');
        th.textContent = key;
        headerRow.appendChild(th);
    });
    let thDelete = document.createElement('th');
    thDelete.textContent = 'Actions'; // Header for delete button column
    headerRow.appendChild(thDelete);
    table.appendChild(headerRow);

    // Populate table rows
    data.forEach(row => {
        let tr = document.createElement('tr');
        Object.entries(row).forEach(([key, value]) => {
            let td = document.createElement('td');
            let input = document.createElement('input'); // Use input for editable cells
            input.type = 'text';
            input.value = value !== null ? value : '';
            input.setAttribute('data-column', key); // Store column name for identification
            input.addEventListener('change', function(e) {
                row[key] = e.target.value; // Update row data on change
            });
            td.appendChild(input);
            tr.appendChild(td);
        });

        // Create delete button for each row
        let tdDelete = document.createElement('td');
        let deleteBtn = document.createElement('button');
        deleteBtn.textContent = 'Delete';
        deleteBtn.className = 'btn btn-danger btn-sm'; // Bootstrap classes for button styling
        deleteBtn.addEventListener('click', function() {
            // Remove the row from the data array
            let index = data.indexOf(row);
            data.splice(index, 1);
            // Re-render the table
            displayCleanedTable(data);
        });
        tdDelete.appendChild(deleteBtn);
        tr.appendChild(tdDelete);

        table.appendChild(tr);
    });

    // Display the table
    let cleanedTableContainer = document.getElementById('cleanedTableContainer');
    cleanedTableContainer.innerHTML = ''; // Clear existing table
    cleanedTableContainer.appendChild(table);
}








