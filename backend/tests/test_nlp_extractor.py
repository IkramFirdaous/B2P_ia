"""
Tests for NLP Task Extractor
"""
import pytest
from datetime import datetime, timedelta
from app.ml.nlp_task_extractor import TaskExtractor, NLPConfig, TaskEntity


class TestNLPConfig:
    """Test NLP Configuration"""

    def test_default_config(self):
        """Test default configuration values"""
        config = NLPConfig()
        assert config.spacy_model == "fr_core_news_lg"
        assert config.primary_language == "fr"
        assert config.min_confidence == 0.6
        assert len(config.action_verbs_fr) > 0
        assert len(config.action_verbs_en) > 0

    def test_custom_config(self):
        """Test custom configuration"""
        config = NLPConfig(
            spacy_model="en_core_web_lg",
            primary_language="en",
            min_confidence=0.7
        )
        assert config.spacy_model == "en_core_web_lg"
        assert config.primary_language == "en"
        assert config.min_confidence == 0.7


class TestTaskEntity:
    """Test TaskEntity dataclass"""

    def test_task_entity_creation(self):
        """Test creating a TaskEntity"""
        task = TaskEntity(
            text="Développer l'API REST",
            action="développer",
            urgency=4,
            confidence=0.8
        )
        assert task.text == "Développer l'API REST"
        assert task.action == "développer"
        assert task.urgency == 4
        assert task.confidence == 0.8
        assert task.entities == []

    def test_task_entity_with_deadline(self):
        """Test TaskEntity with deadline"""
        deadline = datetime.now() + timedelta(days=3)
        task = TaskEntity(
            text="Complete the report",
            deadline=deadline,
            confidence=0.9
        )
        assert task.deadline == deadline


class TestTaskExtractor:
    """Test TaskExtractor main class"""

    @pytest.fixture
    def extractor(self):
        """Create a TaskExtractor instance for testing"""
        config = NLPConfig(min_confidence=0.5)
        return TaskExtractor(config=config)

    def test_extractor_initialization(self, extractor):
        """Test extractor initializes correctly"""
        assert extractor is not None
        assert extractor.config is not None
        # Note: spaCy model may or may not load depending on installation

    def test_extract_empty_text(self, extractor):
        """Test extraction from empty text"""
        tasks = extractor.extract_tasks("")
        assert tasks == []

        tasks = extractor.extract_tasks("   ")
        assert tasks == []

    def test_extract_simple_task_french(self, extractor):
        """Test extracting a simple French task"""
        text = "Développer l'API REST pour le module de facturation avant vendredi"
        tasks = extractor.extract_tasks(text)

        # Should extract at least one task
        assert len(tasks) >= 1

        # Check first task has expected properties
        task = tasks[0]
        assert isinstance(task, TaskEntity)
        assert len(task.text) > 0
        assert task.confidence > 0

    def test_extract_simple_task_english(self, extractor):
        """Test extracting a simple English task"""
        text = "Create the API documentation before Monday"
        tasks = extractor.extract_tasks(text)

        assert len(tasks) >= 1
        task = tasks[0]
        assert isinstance(task, TaskEntity)

    def test_extract_with_assignee(self, extractor):
        """Test extracting task with assignee"""
        text = "Jean doit préparer la présentation pour la réunion"
        tasks = extractor.extract_tasks(text)

        assert len(tasks) >= 1

    def test_extract_with_urgency(self, extractor):
        """Test urgency detection"""
        text = "Résoudre le bug critique immédiatement"
        tasks = extractor.extract_tasks(text)

        if len(tasks) > 0:
            task = tasks[0]
            # Should detect high urgency
            assert task.urgency >= 4

    def test_detect_deadline_today(self, extractor):
        """Test deadline detection - today"""
        deadline = extractor._detect_deadline("Finir le rapport aujourd'hui")
        assert deadline is not None
        assert deadline.date() == datetime.now().date()

    def test_detect_deadline_tomorrow(self, extractor):
        """Test deadline detection - tomorrow"""
        deadline = extractor._detect_deadline("Send the email tomorrow")
        assert deadline is not None
        expected_date = (datetime.now() + timedelta(days=1)).date()
        assert deadline.date() == expected_date

    def test_detect_deadline_this_week(self, extractor):
        """Test deadline detection - this week"""
        deadline = extractor._detect_deadline("Complete the task this week")
        assert deadline is not None
        # Should be within next 7 days
        assert deadline > datetime.now()
        assert deadline <= datetime.now() + timedelta(days=7)

    def test_detect_deadline_specific_date(self, extractor):
        """Test deadline detection - specific date"""
        deadline = extractor._detect_deadline("Deadline is 25/12/2025")
        assert deadline is not None
        assert deadline.day == 25
        assert deadline.month == 12
        assert deadline.year == 2025

    def test_detect_urgency_levels(self, extractor):
        """Test urgency level detection"""
        # Critical urgency
        urgency = extractor._detect_urgency("This is urgent and critical")
        assert urgency == 5

        # High urgency
        urgency = extractor._detect_urgency("This is important")
        assert urgency == 4

        # Normal urgency
        urgency = extractor._detect_urgency("Regular task")
        assert urgency == 3

        # Low urgency
        urgency = extractor._detect_urgency("Do this when possible")
        assert urgency == 2

    def test_estimate_effort(self, extractor):
        """Test effort estimation"""
        # Complex task
        effort = extractor._estimate_effort("Développer une application complète")
        assert effort >= 4.0

        # Simple task
        effort = extractor._estimate_effort("Envoyer un email")
        assert effort <= 2.0

    def test_calculate_confidence(self, extractor):
        """Test confidence calculation"""
        # High confidence - has action, object, deadline
        confidence = extractor._calculate_confidence(
            text="Développer l'API avant vendredi",
            action="développer",
            obj="API",
            deadline=datetime.now() + timedelta(days=3),
            urgency=4,
            entity_count=2
        )
        assert confidence > 0.6

        # Low confidence - minimal information
        confidence = extractor._calculate_confidence(
            text="Some text",
            action=None,
            obj=None,
            deadline=None,
            urgency=3,
            entity_count=0
        )
        assert confidence < 0.6

    def test_extract_multiple_tasks(self, extractor):
        """Test extracting multiple tasks from text"""
        text = """
        Action Items:
        - Développer l'API REST
        - Tester les fonctionnalités
        - Déployer sur le serveur
        """
        tasks = extractor.extract_tasks(text)

        # Should extract multiple tasks
        assert len(tasks) >= 2

    def test_extract_from_email_format(self, extractor):
        """Test extraction from email-like text"""
        text = """
        Bonjour,

        Pouvez-vous préparer le rapport mensuel avant vendredi ?
        Il faut aussi contacter le client pour la réunion.

        Merci
        """
        tasks = extractor.extract_tasks(text, source_type="email")

        assert len(tasks) >= 1

    def test_extract_from_meeting_notes(self, extractor):
        """Test extraction from meeting notes"""
        text = """
        Meeting Notes - Sprint Planning

        Action Items:
        1. Jean - Développer la nouvelle feature
        2. Marie - Tester l'intégration
        3. Pierre - Mettre à jour la documentation

        Next meeting: Friday
        """
        tasks = extractor.extract_tasks(text, source_type="meeting")

        # Should find action items
        assert len(tasks) >= 2

    def test_confidence_threshold(self, extractor):
        """Test that low confidence tasks are filtered out"""
        # Set high confidence threshold
        extractor.config.min_confidence = 0.9

        # Ambiguous text
        text = "Maybe we could think about possibly doing something"
        tasks = extractor.extract_tasks(text)

        # Should not extract low confidence tasks
        assert len(tasks) == 0

    def test_cache_functionality(self, extractor):
        """Test caching works correctly"""
        extractor.config.enable_caching = True
        extractor.clear_cache()

        text = "Développer l'API REST"

        # First extraction
        tasks1 = extractor.extract_tasks(text)

        # Second extraction (should use cache)
        tasks2 = extractor.extract_tasks(text)

        # Results should be identical
        assert len(tasks1) == len(tasks2)

        # Cache should have entries
        stats = extractor.get_stats()
        assert stats["cache_size"] > 0

    def test_clear_cache(self, extractor):
        """Test cache clearing"""
        extractor.config.enable_caching = True

        text = "Développer l'API"
        extractor.extract_tasks(text)

        assert extractor.get_stats()["cache_size"] > 0

        extractor.clear_cache()
        assert extractor.get_stats()["cache_size"] == 0

    def test_get_stats(self, extractor):
        """Test stats retrieval"""
        stats = extractor.get_stats()

        assert "spacy_available" in stats
        assert "model_loaded" in stats
        assert "cache_size" in stats
        assert "cache_enabled" in stats

    def test_question_filtering(self, extractor):
        """Test that questions are filtered out"""
        text = "Pouvez-vous me dire comment faire cela ?"
        tasks = extractor.extract_tasks(text)

        # Questions should have lower confidence or be filtered
        if len(tasks) > 0:
            assert tasks[0].confidence < 0.7

    def test_min_task_length(self, extractor):
        """Test minimum task length filtering"""
        # Very short text
        text = "Do it"
        tasks = extractor.extract_tasks(text)

        # Should not extract very short tasks
        assert len(tasks) == 0

    def test_max_task_length(self, extractor):
        """Test task text truncation"""
        # Very long text
        long_text = "Développer " + "très " * 50 + "complexe API system"
        tasks = extractor.extract_tasks(long_text)

        if len(tasks) > 0:
            task = tasks[0]
            # Should be truncated to max length
            assert len(task.text) <= extractor.config.max_task_length

    def test_multilingual_support(self, extractor):
        """Test mixed language text"""
        text = """
        Tasks:
        - Développer l'API REST
        - Create the documentation
        - Tester les fonctionnalités
        """
        tasks = extractor.extract_tasks(text)

        # Should extract tasks in both languages
        assert len(tasks) >= 2


class TestRuleBased:
    """Test rule-based fallback extraction"""

    def test_rule_based_extraction(self):
        """Test extraction without spaCy"""
        # Create extractor without spaCy
        config = NLPConfig(min_confidence=0.4)
        extractor = TaskExtractor(config=config)

        # Force rule-based mode
        extractor.nlp = None

        text = "Développer l'API REST avant vendredi"
        tasks = extractor._extract_rule_based(text)

        assert len(tasks) >= 1
        task = tasks[0]
        assert isinstance(task, TaskEntity)

    def test_split_sentences(self):
        """Test sentence splitting"""
        config = NLPConfig()
        extractor = TaskExtractor(config=config)

        text = "First task. Second task! Third task?"
        sentences = extractor._split_sentences(text)

        assert len(sentences) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
