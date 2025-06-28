import openai

# Sample fallback data for insurers – TO BE REPLACED WITH ACTUAL DATA THIS IS JUST AN EXAMPLE
def scrape_sample_reviews(insurer_name):
    sample_data = {
        "Sun Life": [
            "Great service and responsive agents.",
            "Had issues with claim processing times.",
            "Easy to navigate website and helpful support."
        ],
        "Manulife": [
            "Affordable premiums, but hard to reach customer service.",
            "Transparent policies and friendly agents.",
            "Claim process was a bit slow."
        ],
        "Canada Life": [
            "Responsive customer service and competitive rates.",
            "Website could be more intuitive.",
            "Happy with overall coverage and claim turnaround."
        ]
    }
    return sample_data.get(insurer_name, ["No reviews found."])


def analyze_reviews(insurer_name, reviews):
    joined = "\n\n".join(reviews)
    prompt = f"""
Analyze these customer reviews for {insurer_name} and summarize the overall sentiment in bullet points.
Focus on recurring positives and negatives.

Reviews:
{joined}
"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )
    return response.choices[0].message.content.strip()
