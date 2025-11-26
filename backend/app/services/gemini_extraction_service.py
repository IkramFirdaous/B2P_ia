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
   - deadline: Format ISO "YYYY-MM-DDTHH:MM:SS" (null si non mentionné)
   - confidence: 0.0-1.0

3. SENTIMENT:
   - score: -1.0 (très négatif) à 1.0 (très positif)
   - label: "positive", "neutral", ou "negative"
   - reasoning: Explication brève

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
  ],
  "sentiment": {{
    "score": 0.0,
    "label": "neutral",
    "reasoning": "Explication"
  }}
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
        sentiment = extracted_data.get('sentiment', {})
        email_text = self._prepare_email_text(email_data).lower()
        
        cleaned_tasks = []
        for task in tasks:
            if not task.get('title'):
                continue
            
            title = str(task['title']).strip()
            
            # Clean polite phrases
            title = self._clean_task_title(title)
            
            # Parse deadline
            deadline = self._parse_deadline(task.get('deadline'))
            
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
        
        # Validate sentiment
        sentiment_data = self._validate_sentiment(sentiment)
        
        return {
            'tasks': cleaned_tasks,
            'sentiment': sentiment_data
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
        """Parse deadline string to datetime"""
        if not deadline_str:
            return None
        
        try:
            # Try ISO format first
            return datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            pass
        
        try:
            # Try common formats
            for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y']:
                try:
                    return datetime.strptime(deadline_str, fmt)
                except ValueError:
                    continue
        except:
            pass
        
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
    
    def _validate_sentiment(self, sentiment: Dict) -> Dict:
        """Validate and normalize sentiment data"""
        score = sentiment.get('score', 0.0)
        score = max(-1.0, min(1.0, float(score)))
        
        label = sentiment.get('label', 'neutral').lower()
        if label not in ['positive', 'neutral', 'negative']:
            # Infer label from score
            if score > 0.3:
                label = 'positive'
            elif score < -0.3:
                label = 'negative'
            else:
                label = 'neutral'
        
        return {
            'score': score,
            'label': label,
            'reasoning': sentiment.get('reasoning', 'No reasoning provided')[:500]
        }
    
    def _extract_with_fallback(self, email_content: str, email_data: Dict) -> Dict:
        """Fallback extraction using rule-based approach (multilingual)"""
        
        # First, detect promotional/marketing emails
        if self._is_promotional_email(email_content):
            return {
                'tasks': [],
                'sentiment': {
                    'score': 0.0,
                    'label': 'neutral',
                    'reasoning': 'Promotional/marketing email detected'
                }
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
        
        # Sentiment analysis
        sentiment = self._analyze_sentiment_fallback(email_content)
        
        return {
            'tasks': tasks[:5],  # Limit to 5 tasks
            'sentiment': sentiment
        }
    
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
    
    def _analyze_sentiment_fallback(self, email_content: str) -> Dict:
        """Simple rule-based sentiment analysis"""
        content_lower = email_content.lower()
        
        positive_words = ['thank', 'great', 'excellent', 'good', 'merci', 'génial', 'super']
        negative_words = ['urgent', 'problem', 'issue', 'asap', 'problème', 'souci']
        
        positive_count = sum(1 for word in positive_words if word in content_lower)
        negative_count = sum(1 for word in negative_words if content_lower)
        
        if negative_count > positive_count:
            return {'score': -0.3, 'label': 'negative', 'reasoning': 'Negative indicators detected'}
        elif positive_count > negative_count:
            return {'score': 0.3, 'label': 'positive', 'reasoning': 'Positive indicators detected'}
        else:
            return {'score': 0.0, 'label': 'neutral', 'reasoning': 'Neutral tone'}