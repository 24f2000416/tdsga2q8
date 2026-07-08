from fastapi import FastAPI
from pydantic import BaseModel
import re

app = FastAPI()

# -----------------------
# Request Model
# -----------------------

class InvoiceRequest(BaseModel):
    text: str


# -----------------------
# Response Model
# -----------------------

class InvoiceResponse(BaseModel):
    vendor: str
    amount: float
    currency: str
    date: str


# -----------------------
# Extraction Endpoint
# -----------------------

@app.post("/extract", response_model=InvoiceResponse)
def extract(req: InvoiceRequest):

    text = req.text.strip()

    if not text:
        return InvoiceResponse(
            vendor="",
            amount=0,
            currency="",
            date=""
        )

    # -----------------------
    # Vendor
    # -----------------------

    vendor = ""

    vendor_patterns = [
        r"Vendor[:\-]\s*(.+)",
        r"Supplier[:\-]\s*(.+)",
        r"From[:\-]\s*(.+)",
        r"Company[:\-]\s*(.+)",
    ]

    for pattern in vendor_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            vendor = match.group(1).split("\n")[0].strip()
            break


    currency = ""
    match = re.search(r"\b(USD|EUR|GBP)\b", text, re.IGNORECASE)
    if match:
        currency = match.group(1).upper()


    amount = 0.0

    match = re.search(r"(\d+(?:,\d{3})*(?:\.\d+)?)", text)

    if match:
        try:
            amount = float(match.group(1).replace(",", ""))
        except ValueError:
            amount = 0.0


    date = ""

    match = re.search(r"\d{4}-\d{2}-\d{2}", text)

    if match:
        date = match.group(0)

    return InvoiceResponse(
        vendor=vendor,
        amount=amount,
        currency=currency,
        date=date
    )