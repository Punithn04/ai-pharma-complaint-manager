"""Generate realistic sample pharmaceutical complaint documents.

Fictional data for demonstration only. Produces:
  - amoxicillin_complaint.pdf   (Finished Dosage Form / FDF example)
  - metformin_api_complaint.pdf (Active Pharmaceutical Ingredient / API example)
  - complaint_email.eml         (plain-text email intake example)

Run:  python sample_data/generate.py
"""
import os

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

HERE = os.path.dirname(os.path.abspath(__file__))


def _pdf(filename: str, lines: list[str]) -> None:
    path = os.path.join(HERE, filename)
    doc = SimpleDocTemplate(path, pagesize=A4, topMargin=20 * mm, bottomMargin=20 * mm)
    styles = getSampleStyleSheet()
    story = []
    for line in lines:
        if line == "":
            story.append(Spacer(1, 6))
        elif line.startswith("# "):
            story.append(Paragraph(line[2:], styles["Title"]))
        elif line.startswith("## "):
            story.append(Paragraph(line[3:], styles["Heading2"]))
        else:
            story.append(Paragraph(line, styles["BodyText"]))
    doc.build(story)
    print("wrote", path)


AMOXICILLIN = [
    "# Product Quality Complaint Report",
    "## Finished Dosage Form (FDF)",
    "",
    "<b>Complaint Source:</b> Apollo Pharmacy, Chennai (Retail Distributor)",
    "<b>Customer Name:</b> Apollo Pharmacy Ltd.",
    "<b>Date Reported:</b> 2026-07-18",
    "",
    "<b>Product Name:</b> Amoxicillin Capsules",
    "<b>Strength:</b> 500 mg",
    "<b>Batch/Lot Number:</b> AMX26014",
    "<b>Manufacturing Date:</b> 2026-01-10",
    "<b>Expiry Date:</b> 2028-01-09",
    "<b>Quantity Affected:</b> 30 capsules (2 blister strips)",
    "",
    "<b>Complaint Type:</b> Quality Defect - Discoloration",
    "<b>Description:</b> The pharmacist reported that several Amoxicillin 500 mg "
    "capsules in the received batch showed visible discoloration, with the capsule "
    "shell appearing patchy brown instead of the usual white/opaque finish. No "
    "adverse patient events were reported. The affected strips were quarantined and "
    "returned for investigation.",
]

METFORMIN = [
    "# Customer Complaint Notification",
    "## Active Pharmaceutical Ingredient (API)",
    "",
    "<b>Complaint Source:</b> Zydus Formulations (B2B API Customer)",
    "<b>Customer Name:</b> Zydus Formulations Pvt. Ltd.",
    "<b>Date Reported:</b> 2026-07-12",
    "",
    "<b>Product Name:</b> Metformin Hydrochloride API",
    "<b>Grade:</b> IP/BP",
    "<b>Batch/Lot Number:</b> MFH260712A",
    "<b>Manufacturing Date:</b> 2026-07-01",
    "<b>Retest Date:</b> 2029-06-30",
    "<b>Quantity Affected:</b> 25 kg (1 HDPE drum)",
    "",
    "<b>Complaint Type:</b> Contamination - Foreign Particulate Matter",
    "<b>Description:</b> During pre-dispensing inspection, the customer's QC team "
    "observed black foreign particulate matter in one HDPE drum of Metformin "
    "Hydrochloride API. The drum was sealed on receipt. Sample retained for "
    "investigation; the customer has requested a root-cause investigation and "
    "batch disposition.",
]


EMAIL = """\
From: quality@medplus-distribution.com
To: complaints@aivoa-pharma.com
Subject: Complaint - Pantoprazole Tablets 40mg - broken tablets

Hello Quality Team,

We are writing to report a complaint regarding Pantoprazole Gastro-resistant
Tablets 40 mg, batch PNT25330, received at our Hyderabad warehouse.

On opening the shipment we found that approximately 60 tablets across 5 strips
were cracked or broken. Manufacturing date on the pack is 2025-11-20 and the
expiry is 2027-11-19. No discoloration was observed, only physical breakage.

This appears to be a packaging / mechanical damage issue. Please advise on
returns and replacement.

Regards,
Priya Menon
QA Officer, MedPlus Distribution
"""


def main() -> None:
    _pdf("amoxicillin_complaint.pdf", AMOXICILLIN)
    _pdf("metformin_api_complaint.pdf", METFORMIN)
    with open(os.path.join(HERE, "complaint_email.eml"), "w", encoding="utf-8") as fh:
        fh.write(EMAIL)
    print("wrote", os.path.join(HERE, "complaint_email.eml"))


if __name__ == "__main__":
    main()
