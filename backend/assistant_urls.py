"""
URL routes for the Payroll AI Assistant API.
"""

from django.urls import path
from assistant_api import (
    AssistantQueryView,
    AssistantCategoriesView,
    AssistantTaxYearsView,
    AssistantKnowledgeBaseStatusView,
    AssistantUpdatesView,
    query_with_filter,
    simulate_update,
    export_knowledge_base,
    import_knowledge_base,
)

urlpatterns = [
    path('query/', AssistantQueryView.as_view(), name='assistant-query'),
    path('query-filtered/', query_with_filter, name='assistant-query-filtered'),
    path('categories/', AssistantCategoriesView.as_view(), name='assistant-categories'),
    path('tax-years/', AssistantTaxYearsView.as_view(), name='assistant-tax-years'),
    path('status/', AssistantKnowledgeBaseStatusView.as_view(), name='assistant-status'),
    path('updates/', AssistantUpdatesView.as_view(), name='assistant-updates'),
    path('simulate-update/', simulate_update, name='assistant-simulate-update'),
    path('export/', export_knowledge_base, name='assistant-export'),
    path('import/', import_knowledge_base, name='assistant-import'),
]