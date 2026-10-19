from typing import Literal, Optional

from pydantic import BaseModel, Field


class ExtractedField(BaseModel):
    name: str = Field(description="Short snake_case field name")
    value: str = Field(default="", description="Extracted value; empty if absent")
    type: Literal["text", "date", "amount", "id", "name", "address", "other"] = "text"
    confidence: float = Field(default=0.5, ge=0, le=1, description="0 to 1")
    source_quote: str = Field(default="", description="Exact supporting text copied from the document")
    grounded: Optional[bool] = Field(default=None, description="Set by the backend; leave unset")
    reviewed: Optional[bool] = Field(default=None, description="Set by the user; leave unset")


class LineItem(BaseModel):
    description: str = ""
    quantity: str = ""
    unit_price: str = ""
    total: str = ""


class Check(BaseModel):
    level: Literal["ok", "warn", "error"] = "warn"
    message: str = ""


class DocumentExtraction(BaseModel):
    document_type: str
    summary: str
    fields: list[ExtractedField]
    line_items: list[LineItem] = []
    missing_or_uncertain: list[str] = []
    checks: list[Check] = Field(default=[], description="Set by the backend; leave empty")
    masked_text: Optional[str] = Field(default=None, description="Set by the backend; leave unset")


class StructureRequest(BaseModel):
    text: str
    template: str = "auto"
    redact: bool = False


class AskRequest(BaseModel):
    text: str
    question: str
    history: list[dict[str, str]] = []
    redact: bool = False


class BatchItem(BaseModel):
    filename: str = ""
    extraction: DocumentExtraction


class BatchExport(BaseModel):
    documents: list[BatchItem]
