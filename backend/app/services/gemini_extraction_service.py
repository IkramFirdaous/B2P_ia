"""Gemini API Service - LLM-based Email Extraction (IMPROVED VERSION)"""
import json
import re
from typing import Dict, List, Optional
from datetime import datetime, timedelta

try:
    import google.generativeai as genai
except ImportError:
    genai = None

from app.core.config import settings


class GeminiExtractionService:
    """Service for extracting information from emails using Gemini LLM"""
    
    # Urgency keywords mapping
    URGENCY_KEYWORDS = {
        5: ['immédiatement', 'immediately', 'asap', 'as soon as possible', 'tout de suite', 'right now', 'critique', 'critical'],
        4: ['urgent', 'urgente', 'aujourd\'hui', 'today', 'demain', 'tomorrow', 'dans les 24h', 'within 24h'],
        3: ['cette semaine', 'this week', 'bientôt', 'soon', 'prochainement', 'shortly'],
        2: ['quand tu peux', 'when you can', 'dès que possible', 'when possible'],
    }
    
    def __init__(self):
        if genai and settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            # Configuration optimisée pour des réponses JSON structurées
            generation_config = {
                "temperature": 0.1,  # Très basse pour plus de cohérence
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 2048,
            }
            self.model = genai.GenerativeModel(
                settings.GEMINI_MODEL,
                generation_config=generation_config
            )
        else:
            self.model = None
            print("Warning: Gemini API not configured. Email extraction will use fallback mode.")
    
    def extract_from_email(self, email_data: Dict) -> Dict:
        """
        Extract tasks, deadlines, priorities, and sentiment from email
        
        Args:
            email_data: Dictionary containing email fields (subject, body, sender, etc.)
            
        Returns:
            Dictionary with extracted information
        """
        email_content = self._prepare_email_text(email_data)
        
        if self.model:
            try:
                return self._extract_with_gemini(email_content, email_data)
            except Exception as e:
                print(f"Gemini extraction failed: {e}. Using fallback.")
                return self._extract_with_fallback(email_content, email_data)
        else:
            return self._extract_with_fallback(email_content, email_data)
    
    def _prepare_email_text(self, email_data: Dict) -> str:
        """Prepare email text for extraction"""
        subject = email_data.get('subject', '')
        body = email_data.get('body', '')
        sender = email_data.get('sender', '')
        date = email_data.get('date', datetime.now().isoformat())
        
        return f"""Subject: {subject}
From: {sender}
Date: {date}

{body}""".strip()
    
    def _extract_with_gemini(self, email_content: str, email_data: Dict) -> Dict:
        """Extract using Gemini API with optimized prompt"""
        prompt = self._build_optimized_prompt(email_content)
        
        response = self.model.generate_content(prompt)
        result_text = response.text.strip()
        
        # Parse JSON response avec meilleure extraction
        extracted_data = self._parse_json_response(result_text)
        
        if extracted_data:
            return self._validate_and_format_extraction(extracted_data, email_data)
        else:
            print("Failed to parse Gemini response, using fallback")
            return self._extract_with_fallback(email_content, email_data)
    
    def _build_optimized_prompt(self, email_content: str) -> str:
        """Build an optimized, concise prompt for Gemini API"""
        today = datetime.now().strftime("%Y-%m-%d")
        next_monday = (datetime.now() + timedelta(days=(7 - datetime.now().weekday()))).strftime("%Y-%m-%d")
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        return f"""Tu es un assistant d'extraction de tâches. Analyse cet email et extrais les informations au format JSON stricte.

DATE ACTUELLE: {today}

EMAIL:
{email_content}

RÈGLES D'EXTRACTION:

1. FILTRAGE:
   - REJETTE les emails promotionnels/newsletters (retourne tasks: [])
   - ACCEPTE uniquement les vraies demandes de travail

2. TÂCHES - Format pour chaque tâche:
   - title: Verbe infinitif + objet (ex: "Réviser rapport Q4", "Envoyer fichier")
     * SUPPRIME: "peux-tu", "pourrais-tu", "please", "could you"
     * GARDE: Action claire et objective
   - description: Contexte complet (optionnel)
   - urgency: Nombre 1-5 basé sur:
     * 5 = "immédiatement", "ASAP", "critique"
     * 4 = "urgent", "aujourd'hui", "demain"
     * 3 = "cette semaine", deadline 3-7 jours
     * 2 = "quand tu peux", deadline >7 jours
     * 1 = Pas de deadline, informatif
   - deadline: Extrais la deadline EXACTEMENT comme mentionnée dans l'email
     * Si l'email dit "demain" → mets "{tomorrow}T17:00:00"
     * Si l'email dit "lundi" → mets "{next_monday}T17:00:00"
     * Si l'email dit "aujourd'hui" → mets "{today}T17:00:00"
     * Si l'email donne une date précise (ex: "le 5 décembre") → mets "2024-12-05T17:00:00"
     * Si AUCUNE deadline n'est mentionnée → mets null
   - confidence: 0.0-1.0 (confiance dans l'extraction)

RETOURNE UNIQUEMENT UN OBJET JSON VALIDE (pas de markdown, pas de texte avant/après):
{{
  "tasks": [
    {{
      "title": "Action concise",
      "description": "Contexte détaillé",
      "urgency": 3,
      "deadline": "2024-12-01T17:00:00",
      "confidence": 0.9
    }}
  ]
}}

IMPORTANT: Réponds UNIQUEMENT avec le JSON, rien d'autre."""

    def _parse_json_response(self, response_text: str) -> Optional[Dict]:
        """Parse JSON from LLM response with multiple strategies"""
        
        # Strategy 1: Direct JSON parse
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            pass
        
        # Strategy 2: Extract from markdown code block
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Strategy 3: Find first JSON object
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass
        
        # Strategy 4: Clean common issues
        cleaned = response_text.strip()
        # Remove BOM and invisible characters
        cleaned = cleaned.encode('utf-8', 'ignore').decode('utf-8')
        # Remove trailing commas
        cleaned = re.sub(r',(\s*[}\]])', r'\1', cleaned)
        
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            print(f"All JSON parsing strategies failed. Response: {response_text[:200]}...")
            return None
    
    def _validate_and_format_extraction(self, extracted_data: Dict, email_data: Dict) -> Dict:
        """Validate and clean extracted data with improved urgency detection"""
        
        tasks = extracted_data.get('tasks', [])
        email_text = self._prepare_email_text(email_data).lower()
        
        # Try to extract a global deadline from the email if Gemini missed it
        global_deadline = self._extract_deadline_from_text(email_text)
        
        cleaned_tasks = []
        for task in tasks:
            if not task.get('title'):
                continue
            
            title = str(task['title']).strip()
            
            # Clean polite phrases
            title = self._clean_task_title(title)
            
            # Parse deadline - if Gemini didn't provide one, use the global deadline
            deadline = self._parse_deadline(task.get('deadline'))
            if not deadline and global_deadline:
                deadline = global_deadline
            
            # IMPROVED: Calculate urgency with override logic
            urgency = self._calculate_urgency(
                task.get('urgency', 3),
                deadline,
                email_text,
                title.lower()
            )
            
            cleaned_task = {
                'title': title[:500],
                'description': str(task.get('description', ''))[:2000] if task.get('description') else None,
                'urgency': urgency,
                'deadline': deadline,
                'confidence': max(0.0, min(1.0, float(task.get('confidence', 0.7))))
            }
            cleaned_tasks.append(cleaned_task)
        
        return {
            'tasks': cleaned_tasks
        }
    
    def _clean_task_title(self, title: str) -> str:
        """Clean task title from polite phrases"""
        polite_phrases = [
            'pourrais-tu', 'peux-tu', 'pourriez-vous', 'pouvez-vous',
            'could you', 'can you', 'would you', 'will you',
            'please', 's\'il te plaît', 's\'il vous plaît', 'merci de',
            'il faut que tu', 'il faut que vous', 'il faut',
            'j\'aimerais que tu', 'j\'aimerais que vous',
        ]
        
        title_lower = title.lower()
        for phrase in polite_phrases:
            title_lower = title_lower.replace(phrase, '')
        
        # Reconstruct with proper case (keep original capitalization where possible)
        words = title.split()
        cleaned_words = []
        skip_next = False
        
        for i, word in enumerate(words):
            if skip_next:
                skip_next = False
                continue
            
            word_lower = word.lower()
            # Check if this word is part of a polite phrase
            is_polite = any(phrase.startswith(word_lower) for phrase in polite_phrases)
            
            if not is_polite:
                cleaned_words.append(word)
        
        title = ' '.join(cleaned_words)
        
        # Remove punctuation at the end
        title = re.sub(r'[?!.]+$', '', title).strip()
        
        # Normalize spaces
        title = ' '.join(title.split())
        
        # Capitalize first letter
        if title:
            title = title[0].upper() + title[1:]
        
        return title
    
    def _parse_deadline(self, deadline_str: Optional[str]) -> Optional[datetime]:
        """Parse deadline string to datetime with improved relative date handling"""
        if not deadline_str:
            return None
        
        deadline_str = str(deadline_str).strip()
        
        # Try ISO format first
        try:
            return datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            pass
        
        # Try common date formats
        date_formats = [
            '%Y-%m-%d',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%d %H:%M:%S',
            '%d/%m/%Y',
            '%m/%d/%Y',
            '%d-%m-%Y',
            '%Y/%m/%d'
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(deadline_str, fmt)
            except ValueError:
                continue
        
        # Handle relative dates (fallback)
        deadline_lower = deadline_str.lower()
        now = datetime.now()
        
        # Today/tomorrow
        if 'today' in deadline_lower or "aujourd'hui" in deadline_lower:
            return now.replace(hour=17, minute=0, second=0, microsecond=0)
        if 'tomorrow' in deadline_lower or 'demain' in deadline_lower:
            return (now + timedelta(days=1)).replace(hour=17, minute=0, second=0, microsecond=0)
        
        # Days of week
        weekdays_en = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        weekdays_fr = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']
        
        for i, (en, fr) in enumerate(zip(weekdays_en, weekdays_fr)):
            if en in deadline_lower or fr in deadline_lower:
                days_ahead = (i - now.weekday()) % 7
                if days_ahead == 0:
                    days_ahead = 7  # Next week
                target_date = now + timedelta(days=days_ahead)
                return target_date.replace(hour=17, minute=0, second=0, microsecond=0)
        
        return None
    
    def _calculate_urgency(
        self, 
        llm_urgency: int, 
        deadline: Optional[datetime],
        email_text: str,
        task_title: str
    ) -> int:
        """
        Calculate final urgency with intelligent override logic
        Priority: Keywords > Deadline proximity > LLM suggestion
        """
        
        # Start with LLM suggestion (clamped)
        urgency = max(1, min(5, int(llm_urgency)))
        
        # Override 1: Check for urgency keywords in email
        detected_urgency = self._detect_urgency_from_keywords(email_text)
        if detected_urgency > urgency:
            urgency = detected_urgency
        
        # Override 2: Check deadline proximity
        if deadline:
            days_until = (deadline.date() - datetime.now().date()).days
            
            if days_until <= 0:
                urgency = max(urgency, 5)  # Past or today = CRITICAL
            elif days_until == 1:
                urgency = max(urgency, 4)  # Tomorrow = HIGH
            elif days_until <= 3:
                urgency = max(urgency, 3)  # 2-3 days = MEDIUM
            elif days_until <= 7:
                urgency = max(urgency, 3)  # This week = MEDIUM
        
        # Override 3: Check for urgency in task title itself
        title_urgency = self._detect_urgency_from_keywords(task_title)
        if title_urgency > urgency:
            urgency = title_urgency
        
        return max(1, min(5, urgency))
    
    def _detect_urgency_from_keywords(self, text: str) -> int:
        """Detect urgency level from keywords in text"""
        text_lower = text.lower()
        
        # Check from highest to lowest urgency
        for urgency_level in sorted(self.URGENCY_KEYWORDS.keys(), reverse=True):
            keywords = self.URGENCY_KEYWORDS[urgency_level]
            if any(keyword in text_lower for keyword in keywords):
                return urgency_level
        
        return 1  # Default: very low
    
    def _extract_with_fallback(self, email_content: str, email_data: Dict) -> Dict:
        """Fallback extraction using rule-based approach (multilingual)"""
        
        # First, detect promotional/marketing emails
        if self._is_promotional_email(email_content):
            return {
                'tasks': []
            }
        
        tasks = []
        
        # Extract tasks using action verbs
        action_patterns = [
            # French
            (r'(?:peux-tu|pourrais-tu|pourriez-vous|il faut|merci de)\s+(.+?)(?:\?|\.|\n|$)', 'fr'),
            # English
            (r'(?:could you|can you|please|need to)\s+(.+?)(?:\?|\.|\n|$)', 'en'),
        ]
        
        for pattern, lang in action_patterns:
            matches = re.finditer(pattern, email_content, re.IGNORECASE)
            for match in matches:
                task_text = match.group(1).strip()
                title = self._clean_task_title(task_text)
                
                if len(title) > 10:  # Minimum viable task
                    tasks.append({
                        'title': title[:200],
                        'description': None,
                        'urgency': self._detect_urgency_from_keywords(email_content.lower()),
                        'deadline': None,
                        'confidence': 0.5
                    })
        
        return {
            'tasks': tasks[:5]  # Limit to 5 tasks
        }
    
    def _extract_deadline_from_text(self, text: str) -> Optional[datetime]:
        """
        Extract deadline from email text using pattern matching
        This is a fallback when Gemini doesn't detect the deadline
        """
        text_lower = text.lower()
        now = datetime.now()
        
        # Pattern 1: "today" / "aujourd'hui"
        if re.search(r'\b(today|aujourd\'?hui)\b', text_lower):
            return now.replace(hour=17, minute=0, second=0, microsecond=0)
        
        # Pattern 2: "tomorrow" / "demain"
        if re.search(r'\b(tomorrow|demain)\b', text_lower):
            return (now + timedelta(days=1)).replace(hour=17, minute=0, second=0, microsecond=0)
        
        # Pattern 3: Days of the week (next occurrence)
        weekdays = {
            'monday': 0, 'lundi': 0,
            'tuesday': 1, 'mardi': 1,
            'wednesday': 2, 'mercredi': 2,
            'thursday': 3, 'jeudi': 3,
            'friday': 4, 'vendredi': 4,
            'saturday': 5, 'samedi': 5,
            'sunday': 6, 'dimanche': 6
        }
        
        for day_name, day_num in weekdays.items():
            pattern = rf'\b(by|before|for|pour|avant|d\'?ici)\s+{day_name}\b'
            if re.search(pattern, text_lower):
                days_ahead = (day_num - now.weekday()) % 7
                if days_ahead == 0:
                    days_ahead = 7  # Next week
                target_date = now + timedelta(days=days_ahead)
                return target_date.replace(hour=17, minute=0, second=0, microsecond=0)
        
        # Pattern 4: Explicit dates (DD/MM/YYYY, DD-MM-YYYY, YYYY-MM-DD)
        date_patterns = [
            r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',  # DD/MM/YYYY or DD-MM-YYYY
            r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})',  # YYYY-MM-DD
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    if len(match.group(1)) == 4:  # YYYY-MM-DD
                        year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
                    else:  # DD/MM/YYYY
                        day, month, year = int(match.group(1)), int(match.group(2)), int(match.group(3))
                    
                    return datetime(year, month, day, 17, 0, 0)
                except ValueError:
                    continue
        
        # Pattern 5: Relative time ("in 2 days", "dans 3 jours")
        relative_match = re.search(r'(in|dans)\s+(\d+)\s+(day|days|jour|jours)', text_lower)
        if relative_match:
            days = int(relative_match.group(2))
            return (now + timedelta(days=days)).replace(hour=17, minute=0, second=0, microsecond=0)
        
        # Pattern 6: "this week" / "cette semaine"
        if re.search(r'\b(this week|cette semaine)\b', text_lower):
            days_until_friday = (4 - now.weekday()) % 7
            if days_until_friday == 0:
                days_until_friday = 7
            return (now + timedelta(days=days_until_friday)).replace(hour=17, minute=0, second=0, microsecond=0)
        
        # Pattern 7: "end of week" / "fin de semaine"
        if re.search(r'\b(end of (the )?week|fin de (la )?semaine)\b', text_lower):
            days_until_friday = (4 - now.weekday()) % 7
            if days_until_friday == 0:
                days_until_friday = 7
            return (now + timedelta(days=days_until_friday)).replace(hour=17, minute=0, second=0, microsecond=0)
        
        return None
    
    def _is_promotional_email(self, email_content: str) -> bool:
        """Detect if email is promotional/marketing"""
        content_lower = email_content.lower()
        
        promotional_keywords = [
            'unsubscribe', 'opt out', 'discount', 'sale', 'offer',
            'promotion', 'limited time', 'buy now', 'shop now',
            'désabonner', 'réduction', 'solde', 'offre', 'promotion',
            'discover how', 'learn how', 'download now', 'tips and tricks',
            'découvrez comment', 'télécharger maintenant', 'ces conseils'
        ]
        
        promo_count = sum(1 for keyword in promotional_keywords if keyword in content_lower)
        return promo_count >= 2