# Merchant Image Validator Agent

AI-Powered Islamic Compliance Image Validation System

## Overview

This is a complete merchant image validation system that uses Google Gemini Vision AI to analyze images for compliance with Islamic marketing guidelines. The system processes Excel files containing merchant data and image URLs, validates images against strict compliance rules, and generates detailed reports.

## Features

### Module 1: Excel Data Handling
- Intelligent column detection (automatically detects merchant name and image columns)
- Supports various column name variations
- URL validation
- Data extraction and validation

### Module 2: AI Image Validation
- Google Gemini Vision Pro for image analysis
- Comprehensive compliance checking:
  - People in images (clothing, head cover, expressions)
  - Alcohol and beverages
  - Places, hotels, restaurants, beaches
  - Wellness services
  - Pork/meat products
  - Gambling, smoking, drugs
  - Art and entertainment
  - Religious symbols
  - Text/content compliance
  - Weapons and restricted items
- Confidence scoring (HIGH, MEDIUM, LOW)
- Detailed rejection reasons

### Module 3: Results & Reporting
- Dashboard with statistics
- Downloadable Excel reports with validation results
- Summary statistics
- Status tracking (ACCEPTED, REJECTED, REVIEW_REQUIRED)

## Installation

### Prerequisites
- Python 3.8 or higher
- Google Gemini API Key

### Setup Steps

1. **Clone or download the project**

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure API Key**
   - Create a `.env` file in the project root
   - Add your Gemini API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```
   - Get your API key from: https://makersuite.google.com/app/apikey

4. **Run the application**
```bash
python run.py
```

5. **Access the application**
   - Open your browser and go to: `http://localhost:8000`
   - Upload an Excel file with merchant data and image URLs
   - Wait for validation to complete
   - Download the results

## Excel File Format

Your Excel file should contain:
- **Merchant Name**: Column can be named (merchant, merchant_name, business, company, shop, vendor, etc.)
- **Image URL**: Column can be named (image, image_url, img, photo, url, link, etc.)

Example Excel structure:
| Merchant Name | Image URL |
|--------------|-----------|
| ABC Restaurant | https://example.com/image1.jpg |
| XYZ Store | https://example.com/image2.jpg |

The system will intelligently detect these columns even if they have different names.

## API Endpoints

### Upload & Validate
- **POST** `/api/validate` - Upload Excel file and validate images
  - Request: Multipart form data with Excel file
  - Response: Validation results with download link

### Download Results
- **GET** `/api/download/{filename}` - Download validation results Excel file

### Health Check
- **GET** `/health` - Check if the API is running

## Project Structure

```
MIV-FINAL/
├── backend/
│   ├── api/
│   │   └── main.py          # FastAPI application
│   ├── services/
│   │   ├── excel_processor.py    # Module 1
│   │   ├── image_validator.py    # Module 2
│   │   └── result_generator.py   # Module 3
│   ├── config.py            # Configuration
│   └── __init__.py
├── frontend/
│   ├── templates/
│   │   └── index.html       # Dashboard UI
│   └── static/              # Static files
├── uploads/                 # Uploaded Excel files
├── results/                 # Generated result files
├── requirements.txt
├── run.py                   # Main runner
├── .env.example
└── README.md
```

## Compliance Rules

The system validates images against the following rules:

### ✅ ACCEPTED
- Men and women appropriately dressed with neutral expressions
- Women with head cover (hijab) in modest clothing
- Kids (appropriately dressed)
- Hotel/Restaurant images (men only or no humans)
- Halal meat products
- Cinemas and art shows
- Non-alcoholic beverages

### ❌ REJECTED
- Women without head cover
- Men in shorts or tank tops
- Kids in bathing suits
- Alcohol bottles, wine glasses, cocktails
- Swimming pools with people
- Spa, salon services, nail services
- Gambling, smoking, drugs
- Weapons and ammunition
- Religious symbols (Christmas, cross, etc.)
- Banned words (Magic, Love, Lucky, etc.)

### ⚠️ REVIEW REQUIRED
- Gaming/animation content
- Merchant names with banned words
- Ambiguous images

## Technology Stack

- **Backend**: FastAPI, Python
- **AI/ML**: Google Gemini Pro Vision
- **Data Processing**: Pandas, OpenPyXL
- **Image Processing**: Pillow
- **Frontend**: HTML, CSS, JavaScript

## Notes

- The validation process may take some time depending on the number of images
- Each image is analyzed using AI, so processing multiple images will take time
- Results are saved in the `results/` folder
- Uploaded files are stored in the `uploads/` folder

## Troubleshooting

### API Key Error
- Make sure your `.env` file exists and contains the correct API key
- Verify the key is valid on Google's API website

### Image Download Failures
- Check if image URLs are accessible
- Some URLs may require authentication or have restrictions

### Excel Reading Errors
- Ensure the Excel file is not corrupted
- Check that columns contain valid data

## License

This project is proprietary software.

## Support

For issues or questions, please contact the development team.

