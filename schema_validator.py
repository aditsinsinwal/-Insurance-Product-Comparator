import json

REQUIRED_FIELDS = {
    "Coverage Details",
    "Exclusions",
    "Premium Structure",
    "Waiting Periods",
    "Maximum and Minimum Age Limit",
    "Claim Process",
    "Policy Term"
}

def validate_json_fields(json_text):
    try:
        data = json.loads(json_text)
        missing = REQUIRED_FIELDS - set(data.keys())
        return True if not missing else False, list(missing)
    except Exception as e:
        return False, ["Invalid JSON format"]
