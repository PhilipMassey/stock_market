const XLSX = require('xlsx');
const fs = require('fs');
const path = require('path');

// Define the directory path
const directoryPath = '/Users/philipmassey/Downloads/';

// Read all files in the directory
fs.readdir(directoryPath, (err, files) => {
    if (err) {
        return console.error('Unable to scan directory: ' + err);
    }

    // Iterate over each file in the directory
    files.forEach(file => {
        // Check if the file has an .xlsx extension
        if (path.extname(file) === '.xlsx') {
            const filePath = path.join(directoryPath, file);
            //console.log(`Processing file: ${filePath}`);

            // Read the Excel file
            const workbook = XLSX.readFile(filePath);

            // Save the workbook, overwriting the original file
            XLSX.writeFile(workbook, filePath);

            console.log(`File has been overwritten: ${filePath}`);
        }
    });
});