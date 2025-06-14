import openai
from prompts import extraction_prompt

def extract_fields(text):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{
            "role": "user",
            "content": extraction_prompt.replace("{text}", text)
        }],
        temperature=0.2
    )
    return response.choices[0].message.content.strip()

def compare_documents(doc_a, doc_b):
    comparison_prompt = f"""
Compare the two insurance plans below. Focus on differences in coverage, exclusions, premiums, and other terms.

Plan A:
{doc_a}

Plan B:
{doc_b}

Summarize the key differences in a clear, point-wise manner.
"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": comparison_prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content.strip()

