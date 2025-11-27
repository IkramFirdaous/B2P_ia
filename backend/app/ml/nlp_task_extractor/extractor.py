"""
Task Extractor - Main NLP extraction engine using spaCy
"""
from typing import List, Optional, Dict, Tuple, TYPE_CHECKING, Any
from datetime import datetime, timedelta
import re
from dataclasses import dataclass
from functools import lru_cache
import logging

try:
    import spacy
    from spacy.language import Language
    from spacy.tokens import Doc, Span, Token
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    # Define dummy types for type hints when spaCy is not available
    Language = Any
    Doc = Any
    Span = Any
    Token = Any
    logging.warning("spaCy not available. Install with: pip install spacy")

from .config import NLPConfig, default_config


logger = logging.getLogger(__name__)


@dataclass
class TaskEntity:
    """Represents an extracted task with all its components"""
    text: str
    action: Optional[str] = None
    object: Optional[str] = None
    assignee: Optional[str] = None
    deadline: Optional[datetime] = None
    urgency: int = 3
    estimated_effort: Optional[float] = None
    confidence: float = 0.0
    source_sentence: str = ""
    entities: List[Dict] = None

    def __post_init__(self):
        if self.entities is None:
            self.entities = []


class TaskExtractor:
    """
    Advanced NLP-based task extractor using spaCy

    This class provides comprehensive task extraction capabilities including:
    - Named Entity Recognition (NER) for task components
    - Dependency parsing for action-object relationships
    - Deadline extraction and parsing
    - Urgency detection
    - Confidence scoring
    """

    def __init__(self, config: Optional[NLPConfig] = None):
        """
        Initialize the TaskExtractor

        Args:
            config: Configuration object. If None, uses default configuration
        """
        self.config = config or default_config
        self.nlp: Optional[Language] = None
        self._cache: Dict[str, List[TaskEntity]] = {}

        # Initialize spaCy model
        self._load_spacy_model()

    def _load_spacy_model(self):
        """Load spaCy model with error handling"""
        if not SPACY_AVAILABLE:
            logger.error("spaCy is not available. Task extraction will be limited.")
            return

        try:
            # Try to load the configured model
            self.nlp = spacy.load(self.config.spacy_model)
            logger.info(f"Loaded spaCy model: {self.config.spacy_model}")

            # Add custom pipeline components if needed
            self._add_custom_components()

        except OSError as e:
            logger.error(f"Failed to load spaCy model '{self.config.spacy_model}': {e}")
            logger.info("Attempting to load a smaller fallback model...")

            # Try fallback models
            fallback_models = ["fr_core_news_sm", "en_core_web_sm"]
            for model in fallback_models:
                try:
                    self.nlp = spacy.load(model)
                    logger.info(f"Loaded fallback model: {model}")
                    break
                except OSError:
                    continue

            if self.nlp is None:
                logger.error("No spaCy model could be loaded. Please install a model:")
                logger.error("  python -m spacy download fr_core_news_lg")
                logger.error("  python -m spacy download en_core_web_lg")

    def _add_custom_components(self):
        """Add custom pipeline components to spaCy"""
        if self.nlp is None:
            return

        # Add custom entity ruler for task-specific entities
        if "entity_ruler" not in self.nlp.pipe_names:
            ruler = self.nlp.add_pipe("entity_ruler", before="ner")

            # Add patterns for task-related entities
            patterns = self._create_entity_patterns()
            ruler.add_patterns(patterns)

    def _create_entity_patterns(self) -> List[Dict]:
        """Create entity patterns for task extraction"""
        patterns = []

        # Priority/urgency patterns
        for urgency_level, keywords in self.config.urgency_keywords.items():
            for keyword in keywords:
                patterns.append({
                    "label": "PRIORITY",
                    "pattern": keyword.lower()
                })

        # Action verb patterns
        for verb in self.config.action_verbs_fr + self.config.action_verbs_en:
            patterns.append({
                "label": "TASK_ACTION",
                "pattern": [{"LOWER": verb}]
            })

        return patterns

    def extract_tasks(self, text: str, source_type: str = "email") -> List[TaskEntity]:
        """
        Extract tasks from text

        Args:
            text: Input text to analyze
            source_type: Type of source (email, meeting, chat, etc.)

        Returns:
            List of extracted TaskEntity objects
        """
        if not text or not text.strip():
            return []

        # Check cache
        cache_key = f"{source_type}:{hash(text)}"
        if self.config.enable_caching and cache_key in self._cache:
            return self._cache[cache_key]

        tasks = []

        # Process with spaCy if available
        if self.nlp:
            tasks = self._extract_with_spacy(text, source_type)
        else:
            # Fallback to rule-based extraction
            tasks = self._extract_rule_based(text)

        # Cache results
        if self.config.enable_caching:
            self._manage_cache(cache_key, tasks)

        return tasks

    def _extract_with_spacy(self, text: str, source_type: str) -> List[TaskEntity]:
        """Extract tasks using spaCy NLP pipeline"""
        tasks = []

        # Process text with spaCy
        doc = self.nlp(text)

        # Extract sentences that might contain tasks
        for sent in doc.sents:
            if self._is_task_sentence(sent):
                task = self._parse_task_from_sentence(sent, doc)
                if task and task.confidence >= self.config.min_confidence:
                    tasks.append(task)

        # Extract from action items sections
        action_sections = self._find_action_sections(text)
        for section in action_sections:
            section_tasks = self._extract_from_action_section(section)
            tasks.extend(section_tasks)

        return tasks

    def _is_task_sentence(self, sent: Span) -> bool:
        """
        Determine if a sentence contains a task using NLP analysis

        Args:
            sent: spaCy Span object representing a sentence

        Returns:
            True if the sentence likely contains a task
        """
        # Check for action verbs
        has_action_verb = False
        for token in sent:
            if token.pos_ == "VERB" and token.lemma_.lower() in (
                self.config.action_verbs_fr + self.config.action_verbs_en
            ):
                has_action_verb = True
                break

        if not has_action_verb:
            return False

        # Exclude questions
        if sent.text.strip().endswith("?"):
            return False

        # Check minimum length
        if len(sent) < self.config.min_task_words:
            return False

        # Exclude sentences that are purely informational
        # (e.g., no imperative mood, no modal verbs)
        has_modal = any(token.dep_ in ["aux", "auxpass"] for token in sent)
        has_imperative = any(token.morph.get("Mood") == ["Imp"] for token in sent)

        return has_action_verb and (has_modal or has_imperative or True)

    def _parse_task_from_sentence(self, sent: Span, doc: Doc) -> Optional[TaskEntity]:
        """
        Parse task components from a sentence using dependency parsing

        Args:
            sent: spaCy Span object representing the sentence
            doc: Full document context

        Returns:
            TaskEntity if parsing successful, None otherwise
        """
        # Extract action verb (main verb)
        action = None
        action_token = None
        for token in sent:
            if token.pos_ == "VERB" and token.dep_ in ["ROOT", "ccomp", "xcomp"]:
                action = token.lemma_
                action_token = token
                break

        if not action:
            return None

        # Extract object of the action
        obj = None
        if action_token:
            for child in action_token.children:
                if child.dep_ in ["dobj", "obj", "pobj"]:
                    # Get the full noun phrase
                    obj = self._get_noun_phrase(child)
                    break

        # Extract entities
        entities = []
        assignee = None
        for ent in sent.ents:
            entities.append({
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char
            })

            # Extract assignee (person)
            if ent.label_ in ["PERSON", "PER"] and assignee is None:
                assignee = ent.text

        # Detect deadline
        deadline = self._detect_deadline(sent.text)

        # Detect urgency
        urgency = self._detect_urgency(sent.text)

        # Estimate effort
        effort = self._estimate_effort(sent.text, action)

        # Calculate confidence
        confidence = self._calculate_confidence(
            sent.text,
            action,
            obj,
            deadline,
            urgency,
            len(entities)
        )

        # Create task entity
        task = TaskEntity(
            text=sent.text.strip()[:self.config.max_task_length],
            action=action,
            object=obj,
            assignee=assignee,
            deadline=deadline,
            urgency=urgency,
            estimated_effort=effort,
            confidence=confidence,
            source_sentence=sent.text,
            entities=entities
        )

        return task

    def _get_noun_phrase(self, token: Token) -> str:
        """Extract full noun phrase from a token"""
        # Get all children and descendants
        phrase_tokens = [token]

        # Add adjectives, determiners, compounds
        for child in token.children:
            if child.dep_ in ["amod", "det", "compound", "nummod"]:
                phrase_tokens.append(child)

        # Sort by position and join
        phrase_tokens.sort(key=lambda t: t.i)
        return " ".join([t.text for t in phrase_tokens])

    def _detect_deadline(self, text: str) -> Optional[datetime]:
        """
        Detect and parse deadline from text

        Args:
            text: Text to analyze

        Returns:
            datetime object if deadline found, None otherwise
        """
        text_lower = text.lower()
        today = datetime.now()

        for pattern, deadline_type in self.config.deadline_patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                return self._parse_deadline_match(match, deadline_type, today)

        return None

    def _parse_deadline_match(
        self,
        match: re.Match,
        deadline_type: str,
        today: datetime
    ) -> Optional[datetime]:
        """Parse deadline from regex match"""
        try:
            if deadline_type == "today":
                return today.replace(hour=23, minute=59, second=59)

            elif deadline_type == "tomorrow":
                return (today + timedelta(days=1)).replace(hour=23, minute=59, second=59)

            elif deadline_type == "this_week":
                days_until_friday = (4 - today.weekday()) % 7
                if days_until_friday == 0:
                    days_until_friday = 7
                return (today + timedelta(days=days_until_friday)).replace(
                    hour=23, minute=59, second=59
                )

            elif deadline_type == "next_week":
                days_until_next_friday = ((4 - today.weekday()) % 7) + 7
                return (today + timedelta(days=days_until_next_friday)).replace(
                    hour=23, minute=59, second=59
                )

            elif deadline_type == "in_x_days":
                days = int(match.group(1))
                return (today + timedelta(days=days)).replace(hour=23, minute=59, second=59)

            elif deadline_type in ["before_date", "by_date", "for_date", "date_slash", "date_dash"]:
                date_str = match.group(1) if deadline_type in ["before_date", "by_date", "for_date"] else match.group(0)

                # Try various date formats
                for fmt in ["%d/%m/%Y", "%d-%m-%Y", "%d/%m", "%d-%m"]:
                    try:
                        parsed = datetime.strptime(date_str, fmt)
                        if fmt in ["%d/%m", "%d-%m"]:
                            parsed = parsed.replace(year=today.year)
                            # If date is in the past, assume next year
                            if parsed < today:
                                parsed = parsed.replace(year=today.year + 1)
                        return parsed.replace(hour=23, minute=59, second=59)
                    except ValueError:
                        continue

        except (ValueError, IndexError) as e:
            logger.debug(f"Failed to parse deadline: {e}")

        return None

    def _detect_urgency(self, text: str) -> int:
        """Detect urgency level from text (1-5)"""
        text_lower = text.lower()

        for level in sorted(self.config.urgency_keywords.keys(), reverse=True):
            keywords = self.config.urgency_keywords[level]
            if any(keyword in text_lower for keyword in keywords):
                return level

        return 3  # Default: normal priority

    def _estimate_effort(self, text: str, action: Optional[str] = None) -> float:
        """
        Estimate effort in hours based on task description

        Args:
            text: Task description
            action: Main action verb

        Returns:
            Estimated effort in hours
        """
        text_lower = text.lower()

        # Complex task indicators
        complex_indicators = [
            "développer", "develop", "implement", "créer application",
            "build system", "design architecture", "migrate", "refactor"
        ]

        # Medium complexity indicators
        medium_indicators = [
            "analyser", "analyze", "research", "étudier", "study",
            "préparer", "prepare", "rédiger", "write document"
        ]

        # Simple task indicators
        simple_indicators = [
            "envoyer", "send", "email", "contacter", "contact",
            "vérifier", "check", "valider", "validate", "confirm"
        ]

        # Check indicators
        if any(indicator in text_lower for indicator in complex_indicators):
            return 8.0  # 1 day

        if any(indicator in text_lower for indicator in medium_indicators):
            return 4.0  # Half day

        if any(indicator in text_lower for indicator in simple_indicators):
            return 1.0  # 1 hour

        # Default based on text length
        word_count = len(text.split())
        if word_count > 20:
            return 4.0
        elif word_count > 10:
            return 2.0
        else:
            return 1.0

    def _calculate_confidence(
        self,
        text: str,
        action: Optional[str],
        obj: Optional[str],
        deadline: Optional[datetime],
        urgency: int,
        entity_count: int
    ) -> float:
        """
        Calculate confidence score for task extraction

        Args:
            text: Original text
            action: Extracted action
            obj: Extracted object
            deadline: Extracted deadline
            urgency: Detected urgency
            entity_count: Number of entities found

        Returns:
            Confidence score (0-1)
        """
        confidence = 0.3  # Base confidence

        # Strong indicators
        if action:
            confidence += 0.25

        if obj:
            confidence += 0.15

        if deadline:
            confidence += 0.15

        if urgency in [4, 5]:
            confidence += 0.1

        # More entities = higher confidence
        confidence += min(0.1, entity_count * 0.02)

        # Penalties
        # Very long text might be conversational
        if len(text.split()) > 40:
            confidence -= 0.1

        # Question format reduces confidence
        if text.strip().endswith("?"):
            confidence -= 0.2

        return max(0.0, min(1.0, confidence))

    def _extract_rule_based(self, text: str) -> List[TaskEntity]:
        """
        Fallback rule-based extraction when spaCy is not available

        Args:
            text: Text to analyze

        Returns:
            List of extracted tasks
        """
        tasks = []
        sentences = self._split_sentences(text)

        for sentence in sentences:
            # Check for action verbs
            has_action = any(
                verb in sentence.lower()
                for verb in (self.config.action_verbs_fr + self.config.action_verbs_en)
            )

            if not has_action:
                continue

            # Create basic task
            task = TaskEntity(
                text=sentence[:self.config.max_task_length],
                deadline=self._detect_deadline(sentence),
                urgency=self._detect_urgency(sentence),
                estimated_effort=self._estimate_effort(sentence),
                confidence=0.5,  # Lower confidence for rule-based
                source_sentence=sentence
            )

            if task.confidence >= self.config.min_confidence:
                tasks.append(task)

        return tasks

    def _split_sentences(self, text: str) -> List[str]:
        """Simple sentence splitting"""
        text = re.sub(r'\s+', ' ', text)
        sentences = re.split(r'[.!?\n]+', text)
        return [s.strip() for s in sentences if len(s.strip()) > self.config.min_task_words]

    def _find_action_sections(self, text: str) -> List[str]:
        """Find sections containing action items"""
        patterns = [
            r"(?:action items?|to-?do|next steps?|tasks?):(.+?)(?=\n\n|\Z)",
        ]

        sections = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            sections.extend(matches)

        return sections

    def _extract_from_action_section(self, section_text: str) -> List[TaskEntity]:
        """Extract tasks from action items section"""
        tasks = []

        # Split by bullet points or numbers
        items = re.split(r'[\n\r]+[\s]*[-•*\d.]+[\s]+', section_text)

        for item in items:
            item = item.strip()
            if len(item) < 10:
                continue

            if self.nlp:
                doc = self.nlp(item)
                for sent in doc.sents:
                    task = self._parse_task_from_sentence(sent, doc)
                    if task:
                        # Boost confidence for action section items
                        task.confidence = min(task.confidence + 0.2, 1.0)
                        tasks.append(task)
            else:
                # Rule-based for action items
                task = TaskEntity(
                    text=item[:self.config.max_task_length],
                    deadline=self._detect_deadline(item),
                    urgency=self._detect_urgency(item),
                    estimated_effort=self._estimate_effort(item),
                    confidence=0.7,  # Higher confidence in action sections
                    source_sentence=item
                )
                tasks.append(task)

        return tasks

    def _manage_cache(self, key: str, tasks: List[TaskEntity]):
        """Manage cache with size limit"""
        if len(self._cache) >= self.config.cache_size:
            # Remove oldest entry
            self._cache.pop(next(iter(self._cache)))

        self._cache[key] = tasks

    def clear_cache(self):
        """Clear the extraction cache"""
        self._cache.clear()

    def get_stats(self) -> Dict:
        """Get extraction statistics"""
        return {
            "spacy_available": SPACY_AVAILABLE,
            "model_loaded": self.nlp is not None,
            "model_name": self.config.spacy_model if self.nlp else None,
            "cache_size": len(self._cache),
            "cache_enabled": self.config.enable_caching
        }
