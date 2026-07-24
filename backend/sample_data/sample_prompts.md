# Sample prompts for the demo

Use these in the AI assistant chat to demonstrate each mandatory tool.

## Tool 1 — Log complaint (natural language)
```
Apollo Pharmacy reported discolored capsules in Amoxicillin capsules 500 mg
```

## Tool 2 — Edit complaint (correction, must preserve other fields)
```
Sorry, the batch number is BMX24602 and the affected quantity is 48 capsules
```

## Tool 3 — Document extraction
Upload `sample_data/metformin_api_complaint.pdf` (or `amoxicillin_complaint.pdf`,
or `complaint_email.eml`). Then correct it via chat:
```
Sorry, the batch number is CHG260712A and the affected quantity is 50 kg / 2 HDPE drums
```

## Extra — Question answering
```
What severity did you assign and why?
```
