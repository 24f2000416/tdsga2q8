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

    patterns = [
        r"Vendor[:\-]\s*(.+)",
        r"From[:\-]\s*(.+)",
        r"Supplier[:\-]\s*(.+)"
    ]

    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)

        if m:
            vendor = m.group(1).split("\n")[0].strip()
            break

    # -----------------------
    # Currency
    # -----------------------

    currency = ""

    m = re.search(r"\b(USD|EUR|GBP)\b", text)

    if m:
        currency = m.group(1)

    # -----------------------
    # Amount
    # -----------------------

    amount = 0

    m = re.search(
        r"(?:Total|Amount|Due|Total Due)[^\d]*([\d,.]+)",
        text,
        re.IGNORECASE
    )

    if m:
        amount = float(
            m.group(1).replace(",", "")
        )

    # -----------------------
    # Date
    # -----------------------

    date = ""

    m = re.search(
        r"(\d{4}-\d{2}-\d{2})",
        text
    )

    if m:
        date = m.group(1)

    return InvoiceResponse(
        vendor=vendor,
        amount=amount,
        currency=currency,
        date=date
    )