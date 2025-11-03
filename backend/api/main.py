"""FastAPI Application - Merchant Image Validator Agent"""
from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Request
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import base64
import uuid
from pathlib import Path
from typing import List
from datetime import datetime

from backend.services.excel_processor import ExcelProcessor
from backend.services.image_validator import ImageValidator
from backend.services.result_generator import ResultGenerator
from backend.config import UPLOAD_DIR

app = FastAPI(title="Merchant Image Validator Agent", version="1.0.0")

# Create images directory for uploaded single images
IMAGES_DIR = Path("uploads/images")
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
os.makedirs("frontend/static", exist_ok=True)

# Mount static files
try:
    app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
except:
    pass  # Ignore if directory doesn't exist


@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint - serve the dashboard"""
    try:
        with open("frontend/templates/index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Dashboard not found. Please check the frontend directory.</h1>", status_code=404)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/api/images/{filename}")
async def serve_image(filename: str):
    """
    Serve uploaded images
    
    Args:
        filename: Image filename
    
    Returns:
        Image file
    """
    image_path = IMAGES_DIR / filename
    if not image_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Determine media type based on file extension
    extension = image_path.suffix.lower()
    media_types = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.webp': 'image/webp',
        '.gif': 'image/gif',
        '.bmp': 'image/bmp'
    }
    media_type = media_types.get(extension, 'image/jpeg')
    
    return FileResponse(
        path=str(image_path),
        media_type=media_type,
        filename=filename
    )


@app.post("/api/upload")
async def upload_excel(file: UploadFile = File(...)):
    """
    Module 1: Upload and process Excel file
    
    Returns:
        Excel processing results
    """
    try:
        # Save uploaded file
        file_path = Path(UPLOAD_DIR) / file.filename
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Process Excel
        processor = ExcelProcessor(str(file_path))
        result = processor.process()
        
        return {
            "success": True,
            "message": "Excel file processed successfully",
            "data": result
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/validate")
async def validate_images(request: Request, file: UploadFile = File(...), compliance_mode: str = Form("sharia")):
    """
    Complete validation pipeline:
    - Module 1: Process Excel
    - Module 2: Validate Images
    - Module 3: Generate Results
    
    Args:
        file: Uploaded file (Excel or image)
        compliance_mode: "sharia" or "general" compliance checking
    
    Returns:
        Validation results
    """
    try:
        # Detect file type
        content_type = file.content_type or ""
        is_image = content_type.startswith("image/")
        is_excel = "excel" in content_type or "spreadsheet" in content_type or \
                   file.filename.endswith(('.xlsx', '.xls'))
        
        if is_image:
            # Handle single image upload
            print("Processing single image file...")
            content = await file.read()
            
            # Save image to file system with unique filename
            file_extension = Path(file.filename).suffix if file.filename else '.jpg'
            if not file_extension or file_extension not in ['.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp']:
                file_extension = '.jpg'
            
            unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}{file_extension}"
            image_file_path = IMAGES_DIR / unique_filename
            
            # Save image file
            with open(image_file_path, "wb") as f:
                f.write(content)
            
            # Generate HTTP URL for the image
            base_url = str(request.base_url).rstrip('/')
            image_http_url = f"{base_url}/api/images/{unique_filename}"
            
            # Also keep base64 for validation processing
            image_base64 = base64.b64encode(content).decode('utf-8')
            image_data_url = f"data:{content_type};base64,{image_base64}"
            
            # Create pseudo Excel data structure with HTTP URL for output
            image_data = [{
                'row_number': 1,
                'merchant_name': 'Single Image Upload',
                'image_url': image_data_url,  # Keep base64 for processing
                'image_http_url': image_http_url,  # HTTP URL for output file
                'is_valid_url': True,
                'is_base64': True,
                'original_data': {
                    'Merchant_Name': 'Single Image Upload',
                    'Merchant_Image': image_http_url  # Use HTTP URL in output
                }
            }]
            
            excel_result = {
                'merchant_column': 'Merchant_Name',
                'image_column': 'Merchant_Image'
            }
            
        elif is_excel:
            # Handle Excel file (existing logic)
            file_path = Path(UPLOAD_DIR) / file.filename
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)
            
            # Module 1: Process Excel
            print("Processing Excel file...")
            processor = ExcelProcessor(str(file_path))
            excel_result = processor.process()
            
            # Extract image URLs
            image_data = excel_result['data']
        else:
            raise HTTPException(status_code=400, detail="Invalid file type. Please upload an Excel file or an image.")
        
        image_urls = [item['image_url'] for item in image_data if item.get('is_valid_url') or item.get('is_base64')]
        
        # Module 2: Validate Images
        print(f"Validating {len(image_urls)} images using {compliance_mode} compliance mode...")
        validator = ImageValidator(compliance_mode=compliance_mode)
        
        validation_results = []
        for i, item in enumerate(image_data):
            if item.get('is_base64'):
                # Handle base64 image (from single image upload)
                print(f"Validating image {i+1}/{len(image_urls)}: base64 image")
                image_url = item['image_url']
                # Extract base64 part
                base64_data = image_url.split(',')[1]
                image_bytes = base64.b64decode(base64_data)
                result = validator.analyze_image(image_bytes)
                validation_results.append(result)
            elif item.get('is_valid_url'):
                print(f"Validating image {i+1}/{len(image_urls)}: {item['image_url']}")
                result = validator.validate_image_url(item['image_url'])
                validation_results.append(result)
            else:
                # Invalid URL
                validation_results.append({
                    'url': item['image_url'],
                    'validated': False,
                    'status': 'REJECTED',
                    'reason': 'Invalid URL format',
                    'confidence': 'HIGH',
                    'confidence_score': 0.95
                })
        
        # Module 3: Generate Results
        print("Generating results...")
        result_generator = ResultGenerator()
        
        # Create Excel file with results
        result_file_path = result_generator.create_result_excel(
            image_data,
            validation_results,
            excel_result
        )
        
        # Create dashboard data
        dashboard_data = result_generator.create_dashboard_data(validation_results)
        
        # Prepare detailed results for preview
        detailed_results = []
        for i, (item, validation) in enumerate(zip(image_data, validation_results)):
            # Get merchant ID and name from original data
            orig_data = item.get('original_data', {})
            
            # Debug: Print available columns on first row
            if i == 0:
                print(f"Available columns in first row: {list(orig_data.keys())}")
            
            # Try to get merchant ID
            merchant_id = (
                orig_data.get('Merchant_ID') or 
                orig_data.get('merchant_id') or 
                orig_data.get('ID') or
                orig_data.get('id') or
                'N/A'
            )
            
            # Try to get merchant name (for reference)
            merchant_name = item.get('merchant_name', '')
            if not merchant_name:
                merchant_name = (
                    orig_data.get('Merchant Name') or 
                    orig_data.get('merchant_name') or 
                    orig_data.get('Merchant') or 
                    orig_data.get('merchant') or 
                    orig_data.get('Offer Name') or
                    orig_data.get('offer_name') or 
                    orig_data.get('business') or 
                    orig_data.get('company') or 
                    orig_data.get('shop') or 
                    orig_data.get('vendor') or
                    'N/A'
                )
            
            # Debug: Print what we found
            if i == 0:
                print(f"Merchant ID extracted: {merchant_id}")
                print(f"Merchant name extracted: {merchant_name}")
            
            detailed_results.append({
                'row': i + 1,
                'merchant': merchant_id,  # Use ID instead of name
                'merchant_name': merchant_name,  # Keep name as reference
                'url': item.get('image_url', ''),
                'status': validation.get('status', 'REVIEW_REQUIRED'),
                'reason': validation.get('reason', 'No reason provided'),
                'confidence_score': validation.get('confidence_score', 0.70)
            })
        
        return {
            "success": True,
            "message": "Validation completed",
            "result_file": result_file_path,
            "dashboard_data": dashboard_data,
            "detailed_results": detailed_results,
            "summary": {
                "total": len(validation_results),
                "accepted": sum(1 for r in validation_results if r.get('status') == 'ACCEPTED'),
                "rejected": sum(1 for r in validation_results if r.get('status') == 'REJECTED'),
                "review_required": sum(1 for r in validation_results if r.get('status') == 'REVIEW_REQUIRED')
            }
        }
    
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


@app.get("/api/download")
async def download_result(filename: str):
    """
    Download result file
    
    Args:
        filename: Name of the result file (can include path)
    """
    try:
        from urllib.parse import unquote
        
        print(f"Download request received for: {filename}")
        
        # Decode the filename to handle URL encoding
        decoded_filename = unquote(filename)
        print(f"Decoded filename: {decoded_filename}")
        
        # Handle different path formats
        if '/' in decoded_filename or '\\' in decoded_filename:
            # If it contains path separators, extract just the filename
            file_name = Path(decoded_filename).name
            file_path = Path("results") / file_name
        else:
            # Otherwise, assume it's just the filename
            file_path = Path("results") / decoded_filename
        
        print(f"Looking for file at: {file_path}")
        print(f"File exists: {file_path.exists()}")
        
        if not file_path.exists():
            print(f"File not found: {file_path}")
            # List available files in results directory
            if Path("results").exists():
                available_files = list(Path("results").glob("*.xlsx"))
                print(f"Available files in results directory: {[str(f) for f in available_files]}")
            
            # Try to find the most recent file
            if available_files:
                latest_file = max(available_files, key=lambda f: f.stat().st_mtime)
                print(f"Using most recent file instead: {latest_file}")
                file_path = latest_file
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
        
        print(f"Serving file: {file_path}")
        return FileResponse(
            path=str(file_path),
            filename=file_path.name,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Download error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/dashboard/{filename}")
async def get_dashboard_data(filename: str):
    """
    Get dashboard data for a specific validation result
    
    Args:
        filename: Name of the result file (optional)
    """
    try:
        # This would typically load dashboard data from stored results
        # For now, return example data
        return {
            "success": True,
            "message": "Dashboard data loaded"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
