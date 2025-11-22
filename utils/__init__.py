"""
Utility modules for the research assistant
"""
from .state import (
    ResearchState,
    UserContext,
    UserCompanyResearch,
    FollowUpAnswers,
    create_initial_state
)

__all__ = [
    'ResearchState',
    'UserContext',
    'UserCompanyResearch',
    'FollowUpAnswers',
    'create_initial_state'
]