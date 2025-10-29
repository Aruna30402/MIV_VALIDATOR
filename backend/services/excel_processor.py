"""Module 1: Excel Data Handling Service"""
import pandas as pd
import re
from typing import Dict, List, Tuple
from pathlib import Path


class ExcelProcessor:
    """Intelligent Excel file processor for merchant data"""
    
    # Possible column name variations
    MERCHANT_NAME_VARIANTS = [
        'merchant_name', 'merchant name', 'merchant', 'business', 'business_name', 
        'business name', 'company', 'company_name', 'company name', 'name', 'shop',
        'shop_name', 'shop name', 'vendor', 'vendor_name', 'vendor name', 'offer_name'
    ]
    
    IMAGE_VARIANTS = [
        'image', 'images', 'image_url', 'image url', 'img', 'image_link', 
        'image link', 'photo', 'photos', 'photo_url', 'photo url', 'picture',
        'pictures', 'url', 'link', 'image_path', 'image path'
    ]
    
    def __init__(self, file_path: str):
        """
        Initialize Excel processor
        
        Args:
            file_path: Path to the Excel file
        """
        self.file_path = Path(file_path)
        self.df = None
        self.merchant_col = None
        self.image_col = None
        
    def load_excel(self) -> pd.DataFrame:
        """
        Load Excel file into DataFrame
        
        Returns:
            DataFrame with loaded data
        """
        try:
            # Try reading as Excel
            self.df = pd.read_excel(self.file_path, engine='openpyxl')
            return self.df
        except Exception as e:
            raise Exception(f"Error loading Excel file: {str(e)}")
    
    def detect_columns(self) -> Tuple[str, str]:
        """
        Intelligently detect merchant name and image columns
        
        Returns:
            Tuple of (merchant_column, image_column)
        """
        if self.df is None:
            raise Exception("Excel file not loaded. Call load_excel() first.")
        
        columns = [col.lower().strip() for col in self.df.columns]
        
        # Find merchant column - prioritize name over ID
        merchant_col = None
        for col in self.df.columns:
            col_lower = col.lower().strip()
            # Skip ID columns explicitly
            if 'id' in col_lower and 'name' not in col_lower:
                continue
            if any(variant in col_lower for variant in self.MERCHANT_NAME_VARIANTS):
                merchant_col = col
                break
        
        # Find image column
        image_col = None
        for col in self.df.columns:
            col_lower = col.lower().strip()
            if any(variant in col_lower for variant in self.IMAGE_VARIANTS):
                image_col = col
                break
        
        # If not found, use first column as merchant, second as image
        if merchant_col is None:
            merchant_col = self.df.columns[0]
        
        if image_col is None:
            # Look for second column
            if len(self.df.columns) > 1:
                image_col = self.df.columns[1]
            else:
                raise Exception("Could not detect image column in Excel file")
        
        self.merchant_col = merchant_col
        self.image_col = image_col
        
        return merchant_col, image_col
    
    def validate_url(self, url: str) -> bool:
        """
        Validate if string is a valid URL
        
        Args:
            url: String to validate
            
        Returns:
            True if valid URL, False otherwise
        """
        if pd.isna(url) or not isinstance(url, str):
            return False
        
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        return bool(url_pattern.match(url.strip()))
    
    def extract_data(self) -> List[Dict]:
        """
        Extract merchant and image data from Excel
        
        Returns:
            List of dictionaries with merchant name and image URL
        """
        if self.df is None or self.merchant_col is None or self.image_col is None:
            raise Exception("Excel not loaded or columns not detected")
        
        data = []
        
        for idx, row in self.df.iterrows():
            merchant_name = str(row[self.merchant_col]) if pd.notna(row[self.merchant_col]) else ""
            image_url = str(row[self.image_col]) if pd.notna(row[self.image_col]) else ""
            
            # Validate image URL
            is_valid_url = self.validate_url(image_url)
            
            data.append({
                'row_number': idx + 1,  # 1-indexed
                'merchant_name': merchant_name,
                'image_url': image_url,
                'is_valid_url': is_valid_url,
                'original_data': row.to_dict()
            })
        
        return data
    
    def process(self) -> Dict:
        """
        Complete processing pipeline
        
        Returns:
            Dictionary containing processed data and metadata
        """
        # Load Excel
        self.load_excel()
        
        # Detect columns
        merchant_col, image_col = self.detect_columns()
        
        # Extract data
        data = self.extract_data()
        
        return {
            'merchant_column': merchant_col,
            'image_column': image_col,
            'total_rows': len(data),
            'valid_urls': sum(1 for d in data if d['is_valid_url']),
            'invalid_urls': sum(1 for d in data if not d['is_valid_url']),
            'data': data,
            'original_columns': self.df.columns.tolist()
        }

