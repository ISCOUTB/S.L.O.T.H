#!/bin/bash

# Script to convert all .xlsx files in tests/data/**/ to .xls format
# Uses LibreOffice headless mode for conversion

echo "Starting conversion of .xlsx files to .xls format..."

# Counter for converted files
converted_count=0
error_count=0

# Find all .xlsx files in tests/data and its subdirectories
while IFS= read -r -d '' xlsx_file; do
    # Get the directory of the current file
    dir_path=$(dirname "$xlsx_file")
    
    # Get the filename without extension
    filename=$(basename "$xlsx_file" .xlsx)
    
    # Create the .xls output path
    xls_file="$dir_path/$filename.xls"
    
    echo "Converting: $xlsx_file -> $xls_file"
    
    # Convert using LibreOffice headless mode
    if libreoffice --headless --convert-to xls:"MS Excel 97" --outdir "$dir_path" "$xlsx_file" > /dev/null 2>&1; then
        echo "✓ Successfully converted: $xlsx_file"
        ((converted_count++))
    else
        echo "✗ Error converting: $xlsx_file"
        ((error_count++))
    fi
    
done < <(find tests/data -name "*.xlsx" -type f -print0)

echo ""
echo "Conversion complete!"
echo "Successfully converted: $converted_count files"
echo "Errors: $error_count files"

if [ $error_count -eq 0 ]; then
    echo "All files converted successfully!"
else
    echo "Some files failed to convert. Check if LibreOffice is installed."
fi
