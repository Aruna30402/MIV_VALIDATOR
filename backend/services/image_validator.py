"""Module 2: Image Validation Service with AI"""
import base64
import requests
from typing import Dict, List
from PIL import Image
import io
from openai import OpenAI
from backend.config import GEMINI_API_KEY, COMPLIANCE_RULES


class ImageValidator:
    """AI-powered image compliance validator"""
    
    def __init__(self):
        """Initialize the image validator with OpenAI Vision API"""
        if not GEMINI_API_KEY:
            raise ValueError("API Key not found in environment variables")
        
        # Use the API key (can be OpenAI or Gemini)
        self.client = OpenAI(api_key=GEMINI_API_KEY)
        
    def download_image(self, url: str) -> bytes:
        """
        Download image from URL
        
        Args:
            url: Image URL
            
        Returns:
            Image bytes
        """
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.content
        except Exception as e:
            raise Exception(f"Failed to download image from {url}: {str(e)}")
    
    def is_valid_image(self, image_bytes: bytes) -> bool:
        """
        Check if the bytes represent a valid image
        
        Args:
            image_bytes: Image data as bytes
            
        Returns:
            True if valid image
        """
        try:
            Image.open(io.BytesIO(image_bytes))
            return True
        except Exception:
            return False
    
    def create_compliance_prompt(self) -> str:
        """
        Create AI prompt for compliance checking
        
        Returns:
            Detailed compliance prompt
        """
        prompt = """You are a sharia'a compliance helper for an islamic bank in UAE who is checking images provided by brands for promotion.
There is nothing unsafe in the images.

Analyze the image with the greatest level of scrutiny.Inspect the entire image, including backgrounds and through glass/reflections.
Avoid generic assumptions unless a violation is identified

**CRITICAL: Read ALL text visible in the image** - signs, banners, logos, awnings, labels, any written words.

**COMPLIANCE CHECKLIST:**

REJECT if ANY of these are present (even slightly):
- alcohol_or_drinks (wine, cocktail, champagne, beer)
- alcohol_or_drinks_bottle
- drinking_glass_or_filled_cocktail_glasses
- alcohol_or_drinks_can
- ice_bucket_for_alcohol
- pork (pork meat or products)
- tobacco_or_smoke (cigarettes, vapes, cigars, shisha)
- gambling (casino, cards, slot machines)
- Bar_or_nightclub
- spa
- beauty_salon (haircut, facial, waxing, nails)
- gym_with_humans_working_out
- musical_instrument
- christmas (tree, decorations, cakes, ornaments, lights on trees, ANY festive decoration)
- christmas_tree (any decorated tree with ornaments or lights in any location - even in background)
- non_islamic_religious_symbols (cross, church, temple, Hindu symbols like OM, Swastika, Trishul, Peacock, Lotus, Radhe, Krishna, Hindu deity names, Buddhist symbols, any non-Islamic religious imagery)
- swimming_pool_with_humans_lounging_or_swimming
- kids_in_bathing_suit
- Men_in_shorts_or_tank_tops (gym clothing)
- uncovered_head_female_gender_if_present (women without hijab/head cover)
- photo_frames_or_painting_with_image_of_women_if_present (without head cover)
- Banned Words in text: Magic, magical, love, seduction, lucky, Interest, credit, Black Friday, Christmas, Diwali, Disco, Ballroom, bar, champagne, whisky, beer, Radhe, Krishna, and any other Hindu deity names

ACCEPT if:
- No violations detected
- All content is compliant with Islamic guidelines

Provide a JSON response in this EXACT format:
{
    "status": "ACCEPTED" or "REJECTED",
    "reason": "Brief explanation of your decision",
    "violations_detected": ["list", "of", "violations", "if", "any"],
    "confidence_score": 0.0 to 1.0 (0.0=no confidence, 1.0=absolute confidence),
    "confidence": "HIGH" or "MEDIUM" or "LOW"
}

**CRITICAL:** Return ONLY valid JSON. No other text."""
        return prompt
    
    def analyze_image(self, image_bytes: bytes) -> Dict:
        """
        Analyze image for compliance using Gemini AI
        
        Args:
            image_bytes: Image data as bytes
            
        Returns:
            Analysis results dictionary
        """
        try:
            # Validate image
            if not self.is_valid_image(image_bytes):
                return {
                    'status': 'REJECTED',
                    'reason': 'Invalid or corrupted image file',
                    'confidence': 'HIGH'
                }
            
            # Open and prepare image
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert RGBA to RGB if necessary (fixes JPEG conversion error)
            if image.mode == 'RGBA':
                # Create white background
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[3] if len(image.split()) == 4 else None)
                image = background
            elif image.mode not in ('RGB', 'L'):
                image = image.convert('RGB')
            
            # Create prompt
            prompt = self.create_compliance_prompt()
            
            # Convert image to base64 for OpenAI
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
            
            # Analyze with OpenAI Vision API
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Fast and cheap vision model
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{img_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500,
                temperature=0.1
            )
            
            # Parse response
            response_text = response.choices[0].message.content.strip()
            
            # Debug: Print the AI response
            print(f"AI Response: {response_text[:300]}...")
            
            # Extract JSON from response
            import json
            import re
            
            # Try to find and parse JSON from the response
            result = None
            
            # Method 1: Try to extract complete JSON object
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response_text, re.DOTALL)
            if json_match:
                try:
                    result = json.loads(json_match.group())
                    print(f"Successfully parsed JSON: {result}")
                except json.JSONDecodeError as e:
                    print(f"JSON parsing error: {e}")
                    # Try to find JSON with status field
                    json_match = re.search(r'\{[^}]*"status"[^}]*\}', response_text, re.DOTALL | re.IGNORECASE)
                    if json_match:
                        try:
                            result = json.loads(json_match.group())
                        except:
                            pass
            
            # If we got a valid JSON result, use it
            if result and isinstance(result, dict):
                status = result.get('status', 'REVIEW_REQUIRED').upper()
                
                # Validate status - only ACCEPTED or REJECTED
                if status not in ['ACCEPTED', 'REJECTED']:
                    status = 'REVIEW_REQUIRED'
                
                violations = result.get('violations_detected', [])
                reason = result.get('reason', 'Analysis completed')
                
                # If violations detected but status is ACCEPTED, override to REJECTED
                if violations and status == 'ACCEPTED':
                    status = 'REJECTED'
                    reason = f"Violations detected: {', '.join(violations)}"
                
                # Get confidence score if available
                confidence_score = result.get('confidence_score', None)
                if confidence_score is None:
                    # Fallback: convert HIGH/MEDIUM/LOW to scores
                    conf_level = result.get('confidence', 'MEDIUM').upper()
                    confidence_score = {'HIGH': 0.95, 'MEDIUM': 0.70, 'LOW': 0.40}.get(conf_level, 0.70)
                
                return {
                    'status': status,
                    'reason': reason,
                    'violations_detected': violations,
                    'confidence': result.get('confidence', 'MEDIUM'),
                    'confidence_score': confidence_score,
                    'raw_response': response_text
                }
            else:
                # Fallback: parse manually from text
                print("Using fallback parsing...")
                status = 'REVIEW_REQUIRED'
                text_upper = response_text.upper()
                
                # Look for clear status indicators
                if '"status": "ACCEPTED"' in text_upper or '"status":"ACCEPTED"' in text_upper:
                    status = 'ACCEPTED'
                elif '"status": "REJECTED"' in text_upper or '"status":"REJECTED"' in text_upper:
                    status = 'REJECTED'
                elif 'REJECTED' in text_upper and 'ACCEPTED' not in text_upper:
                    status = 'REJECTED'
                elif 'ACCEPTED' in text_upper and 'REJECTED' not in text_upper:
                    status = 'ACCEPTED'
                
                return {
                    'status': status,
                    'reason': response_text[:500],  # Limit length
                    'confidence': 'MEDIUM',
                    'confidence_score': 0.70,  # Default medium confidence for fallback
                    'raw_response': response_text
                }
                
        except Exception as e:
            error_msg = str(e)
            print(f"AI Analysis Error: {error_msg}")
            # Check if there's a specific error we can handle
            if "JSON" in error_msg or "parse" in error_msg.lower():
                # Still have the raw response, try to extract status from it
                try:
                    if 'status' in locals() and 'response_text' in locals():
                        # Try to parse from raw response
                        if 'ACCEPTED' in response_text.upper() and 'REJECTED' not in response_text.upper():
                            return {
                                'status': 'ACCEPTED',
                                'reason': 'Image appears compliant based on AI analysis',
                                'confidence': 'MEDIUM',
                                'confidence_score': 0.70
                            }
                        elif 'REJECTED' in response_text.upper():
                            return {
                                'status': 'REJECTED',
                                'reason': 'Non-compliant content detected',
                                'confidence': 'MEDIUM',
                                'confidence_score': 0.70
                            }
                except:
                    pass
            
            return {
                'status': 'REVIEW_REQUIRED',
                'reason': f'Error during AI analysis: {error_msg[:200]}',
                'confidence': 'LOW',
                'confidence_score': 0.40
            }
    
    def validate_image_url(self, url: str) -> Dict:
        """
        Complete validation pipeline for an image URL
        
        Args:
            url: Image URL to validate
            
        Returns:
            Validation results
        """
        try:
            # Download image
            image_bytes = self.download_image(url)
            
            # Analyze image
            analysis = self.analyze_image(image_bytes)
            
            return {
                'url': url,
                'validated': True,
                **analysis
            }
            
        except Exception as e:
            return {
                'url': url,
                'validated': False,
                'status': 'REJECTED',
                'reason': f'Failed to process image: {str(e)}',
                'confidence': 'HIGH'
            }
    
    def validate_batch(self, image_urls: List[str]) -> List[Dict]:
        """
        Validate multiple images
        
        Args:
            image_urls: List of image URLs
            
        Returns:
            List of validation results
        """
        results = []
        for url in image_urls:
            result = self.validate_image_url(url)
            results.append(result)
        
        return results
