"""Gemini AI Service for Task Extraction from Emails"""
from typing import Dict, List
from datetime import datetime, timedelta
import json
import google.generativeai as genai

from app.core.config import settings


class GeminiExtractionService:
    """
    AI-powered task extraction from emails using Gemini

    This service takes email content and uses Gemini AI to:
    1. Extract actionable tasks
    2. Parse deadlines (relative → absolute dates)
    3. Determine urgency levels
    4. Calculate sentiment
    5. Estimate confidence scores
    """

    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not configured")

        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)

    def extract_from_email(self, email_data: Dict) -> Dict:
        """
        Extract tasks from email using Gemini AI

        Args:
            email_data: Dict with keys: subject, sender, content

        Returns:
            Dict with:
                - tasks: List[Dict] with extracted tasks
                - sentiment_score: Float (-1 to 1)
                - sentiment_label: str
        """
        subject = email_data.get('subject', '')
        content = email_data.get('content', '')
        sender = email_data.get('sender', '')

        # Build AI prompt
        prompt = self._build_extraction_prompt(subject, content, sender)

        try:
            # Call Gemini AI
            response = self.model.generate_content(prompt)
            result_text = response.text

            # Strip markdown code blocks if present
            if result_text.strip().startswith('```'):
                # Remove ```json or ``` from start and ``` from end
                lines = result_text.strip().split('\n')
                if lines[0].startswith('```'):
                    lines = lines[1:]  # Remove first line (```json or ```)
                if lines[-1].strip() == '```':
                    lines = lines[:-1]  # Remove last line (```)
                result_text = '\n'.join(lines)

            # Parse JSON response
            result = json.loads(result_text)

            return result

        except json.JSONDecodeError as e:
            # Fallback if JSON parsing fails
            print(f"[WARNING] JSON parsing failed: {e}")
            print(f"[WARNING] Raw text: {result_text[:500]}")
            return {
                'tasks': [],
                'sentiment_score': 0.0,
                'sentiment_label': 'neutral'
            }
        except Exception as e:
            raise RuntimeError(f"Gemini extraction failed: {str(e)}")

    def _build_extraction_prompt(self, subject: str, content: str, sender: str) -> str:
        """Build structured prompt for Gemini AI"""
        today = datetime.now().strftime("%Y-%m-%d")
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

        prompt = f"""You are a task extraction assistant. Analyze this email and extract actionable tasks.

**TODAY'S DATE:** {today}

**EMAIL:**
Subject: {subject}
From: {sender}
Content: {content[:5000]}

**INSTRUCTIONS:**
1. FILTER OUT promotional/newsletter emails → return empty tasks array
2. Extract ONLY actionable work requests (tasks someone needs to do)
3. Ignore greetings, signatures, and filler text
4. For each task extract:
   - title: Clear action verb + object (e.g., "Review Q4 report")
   - description: Full context from email
   - urgency: 1-5 (1=low, 5=critical) based on keywords
   - deadline: Parse relative dates to absolute ISO format
   - confidence: 0.0-1.0 (how confident you are this is a real task)

**URGENCY KEYWORDS:**
- 5 (Critical): "ASAP", "urgent", "immediately", "critical"
- 4 (High): "soon", "today", "this morning"
- 3 (Medium): "this week", "when you can"
- 2 (Low): "eventually", "no rush"
- 1 (Very Low): "someday", "if possible"

**DEADLINE PARSING:**
- "today" → {today}T17:00:00
- "tomorrow" → {tomorrow}T17:00:00
- "this week" → {(datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")}T17:00:00
- "next Monday" → calculate actual date
- No deadline mentioned → null

**SENTIMENT ANALYSIS:**
- Analyze email tone: positive (0.5 to 1.0), neutral (0.0), negative (-1.0 to -0.5)
- Consider: tone, politeness, stress indicators

**OUTPUT FORMAT (ONLY VALID JSON):**
{{
  "tasks": [
    {{
      "title": "Action verb + object",
      "description": "Full context",
      "urgency": 3,
      "deadline": "2024-12-01T17:00:00",
      "confidence": 0.9
    }}
  ],
  "sentiment_score": 0.5,
  "sentiment_label": "positive"
}}

**IMPORTANT:**
- Return ONLY the JSON object, no explanations
- If no tasks found, return empty array: {{"tasks": [], "sentiment_score": 0.0, "sentiment_label": "neutral"}}
- Filter confidence < 0.7 (uncertain tasks)
"""

        return prompt
