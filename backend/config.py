"""Configuration settings for the Image Validator Agent"""
import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
GEMINI_API_KEY = os.getenv("OPENAI_API_KEY", "")  # OpenAI API key

# File Paths
UPLOAD_DIR = "uploads"
RESULTS_DIR = "results"

# Create directories if they don't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# AI Model Configuration
MODEL_NAME = "gemini-1.5-flash"  # Updated model name
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
SUPPORTED_IMAGE_FORMATS = ['.jpg', '.jpeg', '.png', '.webp']

# Compliance Rules
COMPLIANCE_RULES = {
    "images_with_models": {
        "accept": [
            "Men and women appropriately dressed with neutral expressions, with kids",
            "Men and women in the image, with neutral expression, appropriately dressed, but no kid",
            "Women with head cover and in fully covered modest clothing (hijab and abaya)",
            "Kids (boy & girl)"
        ],
        "reject": [
            "Women without hijab/head covered",
            "Men in shorts or tank tops (gym clothing)",
            "Kids in bathing suits"
        ]
    },
    "alcohol": {
        "reject": [
            "Wine or other alcohol bottles",
            "Filled wine glasses or cocktail glasses",
            "Alcohol rack/bar area in restaurant",
            "Ice bucket",
            "Syrup bottles that resemble alcohol bottles",
            "Water bottles or décor objects shaped like alcohol bottles"
        ]
    },
    "places": {
        "reject": [
            "Humans walking, lounging in swimming pools/beaches",
            "Swimming pool with alcohol bottles or filled alcohol glasses",
            "Beach photo without associated hotel/resort",
            "Room/Lobby/Restaurant images with non-compliant objects",
            "Grafitti/Painting/Art/Logo containing banned imagery"
        ],
        "accept": [
            "Hotel lobby/restaurant area with men only customer/staff",
            "Waterparks without human",
            "Hotel/resort images with pool/beach visible (no humans)",
            "Restaurant tables with empty glasses (used for water)",
            "Restaurant image with pool visible in background"
        ]
    },
    "wellness": {
        "reject": [
            "Spa",
            "Salon services (facial, laser, haircut, waxing, eyebrow, cosmetic/aesthetic surgery, threading)",
            "Gyms with women",
            "Nail services"
        ],
        "accept": [
            "Massage tables",
            "Yoga/meditation without women"
        ]
    },
    "pork": {
        "reject": ["Meat image from restaurant serving pork"],
        "accept": ["Meat image from Halal restaurant"]
    },
    "gambling": {
        "reject": [
            "Casino imagery",
            "Bar/Nightclub entrance or bar counter",
            "Sheesha imagery",
            "Vapes/Cigarettes/Cigars/Weed/hemp/any smoking-related products"
        ]
    },
    "art_entertainment": {
        "reject": [
            "Music show or concert",
            "Photos of musical instruments"
        ],
        "accept": [
            "Cinemas",
            "Art shows & exhibitions",
            "Heart shape objects/décor/wall arts"
        ]
    },
    "religious": {
        "reject": [
            "Christmas theme (tree, décor, cakes, etc.)",
            "Cross sign"
        ]
    },
    "words": {
        "reject": [
            "Magic/Magical",
            "Love/Seduction",
            "Lucky",
            "Interest (Lending reference), Credit",
            "Black Friday",
            "Christmas, Diwali, etc.",
            "Disco, Ballroom",
            "Bar",
            "Champagne, margarita, other alcohol-related words"
        ]
    },
    "others": {
        "reject": [
            "Guns/arms & ammunition",
            "Wallet/Payment/EIP brands like Taby",
            "Lending/stock or pawn broking"
        ],
        "review_required": [
            "Gaming or Animation indicating games"
        ]
    }
}
