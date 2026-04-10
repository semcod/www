"""Tests for scoring logic."""

import pytest

pytestmark = [pytest.mark.fast, pytest.mark.unit]
from services.scoring import calculate_health_score, score_to_grade, generate_recommendations


class TestCalculateHealthScore:
    """Test health score calculation."""
    
    def test_perfect_score(self):
        """Test perfect conditions return 100."""
        stats = {"total_lines": 1000}
        complexity = {"cc_avg": 3}
        duplication = {"duplication_groups": 0}
        quality = {"errors": 0, "warnings": 0}
        
        score = calculate_health_score(stats, complexity, duplication, quality)
        assert score == 100
    
    def test_high_complexity_penalty(self):
        """Test high cyclomatic complexity reduces score."""
        stats = {"total_lines": 1000}
        complexity = {"cc_avg": 12}  # Very high
        duplication = {"duplication_groups": 0}
        quality = {"errors": 0, "warnings": 0}
        
        score = calculate_health_score(stats, complexity, duplication, quality)
        assert score == 70  # -30 penalty
    
    def test_duplication_penalty(self):
        """Test duplication groups reduce score."""
        stats = {"total_lines": 1000}
        complexity = {"cc_avg": 5}
        duplication = {"duplication_groups": 15}  # Medium
        quality = {"errors": 0, "warnings": 0}
        
        score = calculate_health_score(stats, complexity, duplication, quality)
        assert score == 85  # -15 penalty
    
    def test_quality_errors_penalty(self):
        """Test errors and warnings reduce score."""
        stats = {"total_lines": 1000}
        complexity = {"cc_avg": 5}
        duplication = {"duplication_groups": 0}
        quality = {"errors": 5, "warnings": 5}  # 5*3 + 5 = 20 penalty, capped at 30
        
        score = calculate_health_score(stats, complexity, duplication, quality)
        assert score == 80  # -20 penalty
    
    def test_small_repo_floor(self):
        """Test very small repos have minimum score of 50."""
        stats = {"total_lines": 50}  # Very small
        complexity = {"cc_avg": 20}  # Would be -30
        duplication = {"duplication_groups": 0}
        quality = {"errors": 0, "warnings": 0}
        
        score = calculate_health_score(stats, complexity, duplication, quality)
        # max(score, 50) ensures small repos don't get penalized too harshly
        assert score >= 50  # Floor protection
    
    def test_score_never_negative(self):
        """Test score is never negative."""
        stats = {"total_lines": 1000}
        complexity = {"cc_avg": 100}  # Extreme
        duplication = {"duplication_groups": 100}  # Extreme
        quality = {"errors": 100, "warnings": 100}  # Extreme
        
        score = calculate_health_score(stats, complexity, duplication, quality)
        assert score >= 0
        assert score <= 100


class TestScoreToGrade:
    """Test grade conversion."""
    
    def test_a_plus(self):
        assert score_to_grade(95) == "A+"
        assert score_to_grade(90) == "A+"
    
    def test_a(self):
        assert score_to_grade(89) == "A"
        assert score_to_grade(80) == "A"
    
    def test_b_plus(self):
        assert score_to_grade(79) == "B+"
        assert score_to_grade(70) == "B+"
    
    def test_b(self):
        assert score_to_grade(69) == "B"
        assert score_to_grade(60) == "B"
    
    def test_c(self):
        assert score_to_grade(59) == "C"
        assert score_to_grade(50) == "C"
    
    def test_d(self):
        assert score_to_grade(49) == "D"
        assert score_to_grade(40) == "D"
    
    def test_f(self):
        assert score_to_grade(39) == "F"
        assert score_to_grade(0) == "F"


class TestGenerateRecommendations:
    """Test recommendation generation."""
    
    def test_high_complexity_recommendation(self):
        complexity = {"cc_avg": 10}
        duplication = {"duplication_groups": 0}
        quality = {"errors": 0}
        
        recs = generate_recommendations(complexity, duplication, quality)
        
        assert len(recs) > 0
        assert any(r["category"] == "complexity" for r in recs)
        assert any(r["priority"] == "high" for r in recs)
    
    def test_duplication_recommendation(self):
        complexity = {"cc_avg": 3}
        duplication = {"duplication_groups": 10, "recoverable_lines": 100}
        quality = {"errors": 0}
        
        recs = generate_recommendations(complexity, duplication, quality)
        
        assert any(r["category"] == "duplication" for r in recs)
    
    def test_quality_errors_recommendation(self):
        complexity = {"cc_avg": 3}
        duplication = {"duplication_groups": 0}
        quality = {"errors": 5}
        
        recs = generate_recommendations(complexity, duplication, quality)
        
        assert any(r["category"] == "quality" for r in recs)
        assert any(r["priority"] == "high" for r in recs)
    
    def test_no_issues_maintenance_message(self):
        complexity = {"cc_avg": 3}
        duplication = {"duplication_groups": 0}
        quality = {"errors": 0}
        
        recs = generate_recommendations(complexity, duplication, quality)
        
        assert len(recs) == 1
        assert recs[0]["category"] == "maintenance"
        assert recs[0]["priority"] == "low"
