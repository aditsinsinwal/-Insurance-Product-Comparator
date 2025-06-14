extraction_prompt = """
Extract the following fields from the insurance document:
1. Coverage Details
2. Exclusions
3. Premium Structure
4. Waiting Periods
5. Maximum and Minimum Age Limit
6. Claim Process
7. Policy Term

Return this in a JSON format with proper field names and short values.
Document Text:
{text}
"""

