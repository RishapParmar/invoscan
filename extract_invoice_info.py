from google.genai import types
from google import genai
import os
from dotenv import load_dotenv 
from datetime import datetime 
from pydantic import BaseModel

# Load environment variables from .env file
load_dotenv()

class Product(BaseModel):
    """
    Represents a product or service item in the invoice.
    """
    name: str
    description: str
    final_price: float
    discount: float

class VendorDetails(BaseModel):
    """
    Contains vendor (sender) information from the invoice.
    """
    company_name: str
    gst_number: str
    address: str
    phone_numbers: list[str]

class CustomerDetails(BaseModel):
    """
    Contains customer (receiver) information from the invoice.
    """
    name: str
    address: str
    phone_numbers: list[str]

class InvoiceDetails(BaseModel):
    """
    Main invoice schema containing all extracted fields.
    """
    bill_number: str
    date_DDMMYY: str
    vendor: VendorDetails
    customer: CustomerDetails
    overall_discount: float
    product_or_service: list[Product]
    total_price_to_pay: float 

def load_file(file_path):
    """
    Loads a file (PDF, PNG, JPEG) and returns its bytes.
    Raises ValueError for unsupported file types.
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext in ['.jpg', '.jpeg', '.png', '.pdf']:
        with open(file_path, 'rb') as f:
            return f.read()
    else:
        raise ValueError("Unsupported file type. Supported: PDF, PNG, JPEG.")

def get_genai_client():
    """
    Initializes and returns a Google Generative AI client using the API key from environment.
    """
    return genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def extract_invoice_info(file_bytes, client, file_path):
    """
    Sends the file bytes to the LLM and extracts invoice information.
    Returns an InvoiceDetails object.
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext in ['.jpg', '.jpeg']:
        mime_type = 'image/jpeg'
    elif ext == '.png':
        mime_type = 'image/png'
    elif ext == '.pdf':
        mime_type = 'application/pdf'
    else:
        raise ValueError("Unsupported file type. Supported: PDF, PNG, JPEG.")

    # Prompt for maximum extraction
    response = client.models.generate_content(
        model='gemini-2.5-flash-lite',
        contents=[
            types.Part.from_bytes(data=file_bytes, mime_type=mime_type),
            (
                "Extract all possible invoice information from the given file. "
                "Include sender and receiver details, company name, GST number, bill number, phone numbers, user name, address, overall discount, all product/service details, "
                "and the total price to pay (after discounts and taxes if present). "
                "Return the result in JSON format matching the InvoiceDetails schema."
            )
        ],
        config={
            "response_mime_type": "application/json",
            "response_schema": InvoiceDetails
        }
    )
    return response.parsed
