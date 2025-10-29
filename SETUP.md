# Setup Guide - Merchant Image Validator Agent

## Quick Start

### Step 1: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Get Gemini API Key
1. Visit: https://makersuite.google.com/app/apikey
2. Create a new API key
3. Copy the API key

### Step 3: Create .env File
Create a file named `.env` in the project root directory:

```
GEMINI_API_KEY=your_actual_api_key_here
```

Replace `your_actual_api_key_here` with your actual API key from Step 2.

### Step 4: Run the Application
```bash
python run.py
```

### Step 5: Access the Dashboard
Open your browser and go to:
```
http://localhost:8000
```

## Testing the System

### Create a Test Excel File

Create an Excel file with the following structure:

| Merchant Name | Image URL |
|--------------|-----------|
| Test Restaurant | https://example.com/image1.jpg |
| Test Store | https://example.com/image2.jpg |

**Note**: Make sure the image URLs are publicly accessible.

### Upload and Validate

1. Go to http://localhost:8000
2. Click "Choose File" and select your Excel file
3. Click "Start Validation"
4. Wait for processing (may take time depending on number of images)
5. View results on the dashboard
6. Download the results Excel file

## Troubleshooting

### Issue: "GEMINI_API_KEY not found"
**Solution**: Make sure the `.env` file exists in the project root and contains your API key.

### Issue: "Failed to download image"
**Solution**: Check that the image URLs in your Excel file are publicly accessible.

### Issue: Port 8000 already in use
**Solution**: Change the port in `run.py`:
```python
uvicorn.run(app, host="0.0.0.0", port=8001)  # Use port 8001
```

## Architecture Overview

### Module 1: Excel Processing (backend/services/excel_processor.py)
- Intelligently detects merchant name and image columns
- Validates image URLs
- Extracts data for processing

### Module 2: Image Validation (backend/services/image_validator.py)
- Downloads images from URLs
- Uses Google Gemini Vision AI to analyze images
- Applies compliance rules
- Returns validation results with reasons

### Module 3: Results Generation (backend/services/result_generator.py)
- Creates downloadable Excel file with results
- Generates dashboard statistics
- Provides summary reports

### API Layer (backend/api/main.py)
- FastAPI endpoints for file upload and validation
- Results download endpoint
- Serves the frontend dashboard

### Frontend (frontend/templates/index.html)
- Modern, responsive UI
- File upload interface
- Progress tracking
- Results dashboard
- Download functionality

## File Structure

```
MIV-FINAL/
├── backend/
│   ├── api/
│   │   └── main.py              # FastAPI application
│   ├── services/
│   │   ├── excel_processor.py   # Module 1
│   │   ├── image_validator.py   # Module 2
│   │   └── result_generator.py  # Module 3
│   └── config.py                # Configuration & compliance rules
├── frontend/
│   └── templates/
│       └── index.html           # Dashboard UI
├── uploads/                     # Uploaded Excel files (auto-created)
├── results/                     # Generated result files (auto-created)
├── requirements.txt             # Python dependencies
├── run.py                       # Application entry point
├── .env                         # API key (you need to create this)
└── README.md                    # Documentation
```

## Next Steps

1. Get your Gemini API key
2. Create the `.env` file with your API key
3. Run `python run.py`
4. Open http://localhost:8000 in your browser
5. Start validating images!

## Support

For issues or questions, refer to the main README.md file or contact the development team.

