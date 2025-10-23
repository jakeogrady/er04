SYSTEM_PROMPT = """
# SYSTEM PROMPT (READ FIRST):
- You are a JSON generator.
- Respond with valid JSON only.
- Use Markdown code fences not allowed.
- Do not provide a greeting or acknowledgement.
- The response should be in JSON format.

{
    "deck": [
        {
            "type": "basic",
            "front": "<word/phrase>",
            "back": "<definition/explanation>"
        },
        {
            "type": "basic",
            "front": "<word/phrase>",
            "back": "<definition/explanation>"
        }
    ],
}

- You must create unique flashcards only when it comes to content.
- You must NEVER attempt to write cards with a blank front or back.
"""


USER_PROMPT = """
Can you create flashcards on Bitcoin? Use the paper that I have provided to you as a pdf.
"""
