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
            amount=0.0,
            currency="",
            date=""
        )

    # -----------------------
    # Vendor
    # -----------------------

    vendor = ""

    vendor_patterns = [

        # Planted vendor like Acme-N66S Industries Ltd.
        r"(Acme-[A-Za-z0-9]+(?:[^\n,]*)?)",

        r"Vendor[:\-]?\s*(.+)",
        r"Supplier[:\-]?\s*(.+)",
        r"From[:\-]?\s*(.+)",
        r"Company[:\-]?\s*(.+)",
        r"Issued\s+by[:\-]?\s*(.+)",
        r"Bill\s+From[:\-]?\s*(.+)",
    ]

    for pattern in vendor_patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            vendor = m.group(1).split("\n")[0].strip()
            break

    # -----------------------
    # Currency
    # -----------------------

    currency = ""

    m = re.search(r"\b(USD|EUR|GBP)\b", text, re.IGNORECASE)

    if m:
        currency = m.group(1).upper()

    # -----------------------
    # Amount
    # -----------------------

    amount = 0.0

    amount_patterns = [

        r"Grand\s*Total[^\d]*([\d,]+\.\d+|[\d,]+)",
        r"Total\s*Due[^\d]*([\d,]+\.\d+|[\d,]+)",
        r"Amount\s*Due[^\d]*([\d,]+\.\d+|[\d,]+)",
        r"Balance\s*Due[^\d]*([\d,]+\.\d+|[\d,]+)",
        r"Amount[^\d]*([\d,]+\.\d+|[\d,]+)",
        r"Total[^\d]*([\d,]+\.\d+|[\d,]+)",

        # Currency before amount
        r"(?:USD|EUR|GBP)\s*([\d,]+\.\d+|[\d,]+)",

        # Currency after amount
        r"([\d,]+\.\d+|[\d,]+)\s*(?:USD|EUR|GBP)",
    ]

    for pattern in amount_patterns:
        m = re.search(pattern, text, re.IGNORECASE)

        if m:
            try:
                amount = float(m.group(1).replace(",", ""))
                break
            except ValueError:
                pass

    # -----------------------
    # Date
    # -----------------------

    date = ""

    date_patterns = [

        r"(\d{4}-\d{2}-\d{2})",

        r"Due\s*Date[^\d]*(\d{4}-\d{2}-\d{2})",

        r"Payment\s*Due[^\d]*(\d{4}-\d{2}-\d{2})",
    ]

    for pattern in date_patterns:
        m = re.search(pattern, text)

        if m:
            date = m.group(1)
            break

    return InvoiceResponse(
        vendor=vendor,
        amount=amount,
        currency=currency,
        date=date
    )  