"""Task Extraction Service - NLP-powered task extraction from text"""
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import re
from app.schemas.task_schema import TaskCandidate
from app.models.task import TaskSource


class TaskExtractionService:
    """Service for extracting tasks from emails, meetings, and other text sources"""

    def __init__(self):
        # Would load spaCy or transformer models here
        # self.nlp = spacy.load("fr_core_news_lg")
        # For now, using rule-based extraction as placeholder

        # Action verbs that indicate tasks (French)
        self.action_verbs_fr = [
            "faire", "créer", "analyser", "préparer", "rédiger", "développer",
            "implémenter", "tester", "réviser", "vérifier", "envoyer", "contacter",
            "organiser", "planifier", "mettre en place", "finaliser", "compléter",
            "documenter", "présenter", "review", "valider"
        ]

        # Action verbs (English)
        self.action_verbs_en = [
            "create", "develop", "implement", "design", "write", "prepare",
            "analyze", "test", "review", "send", "contact", "organize",
            "plan", "setup", "finalize", "complete", "document", "present",
            "validate", "update", "fix", "deploy"
        ]

        # Urgency keywords
        self.urgency_keywords = {
            5: ["urgent", "asap", "immédiat", "critique", "emergency"],
            4: ["important", "prioritaire", "priority", "soon"],
            3: ["normal", "standard"],
            2: ["when possible", "si possible", "low priority"],
            1: ["someday", "eventually", "un jour"]
        }

        # Deadline patterns
        self.deadline_patterns = [
            (r"avant (?:le )?(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})", "before_date"),
            (r"by (\d{1,2}[/-]\d{1,2}[/-]\d{2,4})", "by_date"),
            (r"pour (?:le )?(\d{1,2}[/-]\d{1,2})", "for_date"),
            (r"(aujourd'hui|today)", "today"),
            (r"(demain|tomorrow)", "tomorrow"),
            (r"cette semaine|this week", "this_week"),
            (r"la semaine prochaine|next week", "next_week"),
            (r"dans (\d+) jours?", "in_x_days"),
            (r"in (\d+) days?", "in_x_days")
        ]

    def extract_from_email(self, email_body: str, email_subject: str = "") -> List[TaskCandidate]:
        """Extract tasks from email content"""
        tasks = []

        # Combine subject and body
        full_text = f"{email_subject}\n\n{email_body}"

        # Split into sentences
        sentences = self._split_sentences(full_text)

        for sentence in sentences:
            if self._is_task_sentence(sentence):
                task = self._parse_task_details(sentence)
                if task:
                    tasks.append(task)

        return tasks

    def extract_from_meeting(self, meeting_notes: str, meeting_title: str = "") -> List[TaskCandidate]:
        """Extract action items from meeting notes"""
        tasks = []

        # Look for action items section
        action_sections = self._find_action_sections(meeting_notes)

        if action_sections:
            # Parse action items from dedicated section
            for section in action_sections:
                items = self._parse_action_items(section)
                tasks.extend(items)
        else:
            # Fall back to general sentence analysis
            tasks = self.extract_from_email(meeting_notes, meeting_title)

        return tasks

    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences (simple implementation)"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)

        # Split on sentence boundaries
        sentences = re.split(r'[.!?\n]+', text)

        # Clean and filter
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]

        return sentences

    def _is_task_sentence(self, sentence: str) -> bool:
        """Determine if a sentence contains a task"""
        sentence_lower = sentence.lower()

        # Check for action verbs
        has_action_verb = any(
            verb in sentence_lower
            for verb in self.action_verbs_fr + self.action_verbs_en
        )

        if not has_action_verb:
            return False

        # Exclude questions (usually not tasks)
        if sentence.strip().endswith('?'):
            return False

        # Exclude very short sentences
        if len(sentence.split()) < 4:
            return False

        return True

    def _parse_task_details(self, sentence: str) -> Optional[TaskCandidate]:
        """Extract task details from a sentence"""
        # Extract title (the sentence itself, cleaned)
        title = sentence.strip()

        # Limit title length
        if len(title) > 200:
            title = title[:197] + "..."

        # Detect urgency
        urgency = self._detect_urgency(sentence)

        # Detect deadline
        deadline = self._detect_deadline(sentence)

        # Estimate effort (simple heuristic)
        estimated_effort = self._estimate_effort(sentence)

        # Confidence score (how confident we are this is a real task)
        confidence = self._calculate_confidence(sentence, urgency, deadline)

        return TaskCandidate(
            title=title,
            description=None,  # Could extract more context
            urgency=urgency,
            estimated_effort=estimated_effort,
            deadline=deadline,
            confidence=confidence
        )

    def _detect_urgency(self, text: str) -> int:
        """Detect urgency level from text"""
        text_lower = text.lower()

        for level, keywords in sorted(self.urgency_keywords.items(), reverse=True):
            if any(keyword in text_lower for keyword in keywords):
                return level

        return 3  # Default: normal priority

    def _detect_deadline(self, text: str) -> Optional[datetime]:
        """Extract deadline from text"""
        text_lower = text.lower()

        for pattern, deadline_type in self.deadline_patterns:
            match = re.search(pattern, text_lower)
            if match:
                return self._parse_deadline(match, deadline_type)

        return None

    def _parse_deadline(self, match, deadline_type: str) -> Optional[datetime]:
        """Convert deadline match to datetime"""
        today = datetime.now()

        if deadline_type == "today":
            return today.replace(hour=23, minute=59)
        elif deadline_type == "tomorrow":
            return (today + timedelta(days=1)).replace(hour=23, minute=59)
        elif deadline_type == "this_week":
            # End of current week (Friday)
            days_until_friday = (4 - today.weekday()) % 7
            return (today + timedelta(days=days_until_friday)).replace(hour=23, minute=59)
        elif deadline_type == "next_week":
            # End of next week
            days_until_friday = (4 - today.weekday()) % 7 + 7
            return (today + timedelta(days=days_until_friday)).replace(hour=23, minute=59)
        elif deadline_type == "in_x_days":
            days = int(match.group(1))
            return (today + timedelta(days=days)).replace(hour=23, minute=59)
        elif deadline_type in ["before_date", "by_date", "for_date"]:
            # Parse date (simplified - would need more robust parsing)
            date_str = match.group(1)
            try:
                # Try different date formats
                for fmt in ["%d/%m/%Y", "%d-%m-%Y", "%d/%m", "%d-%m"]:
                    try:
                        parsed = datetime.strptime(date_str, fmt)
                        # If no year, assume current year
                        if fmt in ["%d/%m", "%d-%m"]:
                            parsed = parsed.replace(year=today.year)
                        return parsed.replace(hour=23, minute=59)
                    except:
                        continue
            except:
                pass

        return None

    def _estimate_effort(self, text: str) -> Optional[float]:
        """Estimate effort in hours based on task description"""
        # Very simple heuristic based on keywords
        text_lower = text.lower()

        # Complex task indicators
        complex_keywords = ["développer", "implement", "créer", "analyze", "design"]
        simple_keywords = ["envoyer", "send", "contacter", "contact", "vérifier", "check"]

        if any(keyword in text_lower for keyword in complex_keywords):
            return 4.0  # 4 hours for complex tasks
        elif any(keyword in text_lower for keyword in simple_keywords):
            return 1.0  # 1 hour for simple tasks
        else:
            return 2.0  # Default: 2 hours

    def _calculate_confidence(
        self,
        sentence: str,
        urgency: int,
        deadline: Optional[datetime]
    ) -> float:
        """Calculate confidence that this is a real task"""
        confidence = 0.5  # Base confidence

        # Boost confidence if has clear action verb
        if any(verb in sentence.lower() for verb in self.action_verbs_fr + self.action_verbs_en):
            confidence += 0.2

        # Boost if has deadline
        if deadline:
            confidence += 0.15

        # Boost if has urgency markers
        if urgency >= 4:
            confidence += 0.1

        # Reduce if sentence is very long (might be conversational)
        if len(sentence.split()) > 30:
            confidence -= 0.1

        return min(max(confidence, 0.0), 1.0)

    def _find_action_sections(self, text: str) -> List[str]:
        """Find action items or todo sections in text"""
        sections = []

        # Look for common action item headers
        patterns = [
            r"action items?:(.+?)(?=\n\n|\Z)",
            r"to-?do:(.+?)(?=\n\n|\Z)",
            r"next steps?:(.+?)(?=\n\n|\Z)",
            r"tasks?:(.+?)(?=\n\n|\Z)"
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            sections.extend(matches)

        return sections

    def _parse_action_items(self, section_text: str) -> List[TaskCandidate]:
        """Parse action items from a dedicated section"""
        tasks = []

        # Split by bullet points or numbers
        items = re.split(r'[\n\r]+[\s]*[-•*\d.]+[\s]+', section_text)

        for item in items:
            item = item.strip()
            if len(item) < 10:
                continue

            task = self._parse_task_details(item)
            if task:
                # Boost confidence for items in action section
                task.confidence = min(task.confidence + 0.2, 1.0)
                tasks.append(task)

        return tasks
