# Frontend Testing Guide

## Quick Test Steps

### 1. Access the Dashboard
Open your browser and go to:
```
http://localhost:8000
```

### 2. Upload Test Excel File
1. On the dashboard, click "Choose File"
2. Select `test_data.xlsx` (already created in the project root)
3. Click "Start Validation"

### 3. Wait for Processing
- The system will show a progress bar
- Each image will be analyzed using Gemini AI
- Processing may take 1-3 seconds per image

### 4. View Results
After processing, you'll see:
- **Total Images**: Total number of images validated
- **Accepted**: Images that passed compliance
- **Rejected**: Images that failed compliance
- **Review Required**: Images needing manual review

### 5. Download Results
- Click "📥 Download Results Excel" button
- The Excel file will contain:
  - Original merchant data
  - Status (ACCEPTED/REJECTED/REVIEW_REQUIRED)
  - Reason for rejection
  - Confidence level

## Test Excel File Structure

The test file (`test_data.xlsx`) contains:

| Merchant Name    | Image URL                                |
|------------------|------------------------------------------|
| Test Restaurant  | https://images.unsplash.com/photo-...     |
| Test Store       | https://images.unsplash.com/photo-...     |
| Sample Shop      | https://images.unsplash.com/photo-...     |

## What's Being Tested

### AI Analysis
- Each image is sent to Google Gemini Vision API
- The AI analyzes:
  - People (clothing, head cover, expressions)
  - Alcohol content
  - Places/hotels/restaurants
  - Wellness services
  - Religious symbols
  - Banned text content
  - Weapons and restricted items

### Compliance Rules Applied
- ✅ **ACCEPTED**: Appropriately dressed people, modest clothing, halal products
- ❌ **REJECTED**: Alcohol, inappropriate clothing, banned content
- ⚠️ **REVIEW_REQUIRED**: Ambiguous cases needing human review

## Troubleshooting

### If images fail to download:
- Check internet connection
- Verify image URLs are publicly accessible
- Some URLs may have access restrictions

### If validation is slow:
- Each image requires AI processing
- 3 images should take ~10-30 seconds
- More images = more time

### If results aren't showing:
- Check browser console for errors
- Verify server is running at http://localhost:8000
- Refresh the page and try again

## Expected Results

With the test file, you should see:
- All images processed
- Status assigned to each image
- Detailed reason for rejection/acceptance
- Confidence levels (HIGH/MEDIUM/LOW)

## Creating Your Own Test Data

To test with custom images:

1. Create an Excel file with:
   - Column 1: Merchant Name
   - Column 2: Image URL (publicly accessible)

2. Make sure image URLs are:
   - Publicly accessible (not behind authentication)
   - Valid image formats (JPG, PNG, WEBP)
   - Not too large (< 10MB recommended)

3. Upload through the dashboard interface

## Next Steps

After testing:
1. Try with your own merchant data
2. Review the compliance rules in `backend/config.py`
3. Customize the AI prompt if needed
4. Check the generated Excel reports for detailed analysis

