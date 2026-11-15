import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from retrieval_engine import retrieve_data  # noqa: E402


SUPPORTED_QUESTIONS = [
    "How many rooms does plan 1 have?",
    "How many windows does plan 1 have?",
    "How many doors does plan 1 have?",
    "How many walls does plan 1 have?",
    "What is the largest room in plan 1?",
    "Which room in plan 1 has no windows?",
    "How many rooms does plan 2 have?",
    "How many windows does plan 2 have?",
    "How many doors does plan 2 have?",
    "How many walls does plan 2 have?",
    "What is the largest room in plan 2?",
    "Which room in plan 2 has no windows?",
    "How many rooms does plan 3 have?",
    "How many windows does plan 3 have?",
    "How many doors does plan 3 have?",
    "How many walls does plan 3 have?",
    "What is the average number of rooms across all plans?",
    "Which plans have more than 3 doors?",
    "How many floor plans are in the dataset?",
    "How many components are in the dataset?",
]


@pytest.mark.parametrize("question", SUPPORTED_QUESTIONS)
def test_evaluation_question_is_grounded(question):
    result = retrieve_data(question)
    assert result is not None
    assert result["sql"]
    # An empty result is still grounded: it means the query found no match.
    if "no windows" not in question:
        assert result["evidence"]


@pytest.mark.parametrize(
    "question",
    [
        "What is the rent for plan 1?",
        "What color is the sofa in plan 1?",
    ],
)
def test_unknown_questions_are_declined(question):
    assert retrieve_data(question) is None
