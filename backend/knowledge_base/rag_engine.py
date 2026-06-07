"""
RAG Engine for answering payroll tax questions.
Combines vector search with an LLM-like response generation.
"""

import re
from typing import List, Dict, Any, Optional
from .vector_store import SimpleVectorStore


class RAGEngine:
    """
    Retrieval-Augmented Generation engine for payroll tax queries.
    Uses vector similarity search to find relevant context and generate answers.
    """
    
    def __init__(self, vector_store: SimpleVectorStore):
        """
        Initialize RAG engine with a vector store.
        
        Args:
            vector_store: Initialized vector store with tax documents
        """
        self.vector_store = vector_store
        self._initialize_prompt_templates()
    
    def _initialize_prompt_templates(self):
        """Initialize prompt templates for different query types."""
        self.prompts = {
            'general': """You are a knowledgeable South African payroll tax assistant. 
Based on the following information from the SARS tax database, answer the user's question.

CONTEXT:
{context}

USER QUESTION: {question}

Please provide a clear, accurate answer based on the context above. 
If the information is not in the context, say so and provide general guidance based on known South African tax law.

ANSWER:""",
            
            'bracket_calc': """Calculate the tax for an employee with the following details:

Annual Taxable Income: R{income:,.2f}
Tax Year: {tax_year}
Age Category: {age_category}

Use the following tax brackets from SARS:

{context}

Show the calculation step by step.

CALCULATION:""",
            
            'eti': """The Employment Tax Incentive (ETI) is a government program to encourage employers to hire young workers.

Based on the following ETI rules:

{context}

USER QUESTION: {question}

ETI INFORMATION:"""
        }
    
    def query(
        self, 
        question: str, 
        k: int = 5,
        filter_category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Answer a payroll tax query.
        
        Args:
            question: User's question
            k: Number of context documents to retrieve
            filter_category: Optional category to filter results
            
        Returns:
            Dict with answer, sources, and metadata
        """
        # Retrieve relevant documents
        search_results = self.vector_store.similarity_search(question, k=k)
        
        # Filter by category if specified
        if filter_category:
            search_results = [
                r for r in search_results 
                if r.get('metadata', {}).get('category') == filter_category
            ]
        
        # Build context from results
        context = self._build_context(search_results)
        
        # Determine query type and generate answer
        answer = self._generate_answer(question, context, search_results)
        
        return {
            'answer': answer,
            'sources': [
                {
                    'id': r['id'],
                    'content': r['content'][:200] + '...' if len(r['content']) > 200 else r['content'],
                    'metadata': r['metadata'],
                    'relevance': round(r['similarity'], 3)
                }
                for r in search_results
            ],
            'question': question,
            'num_sources_used': len(search_results)
        }
    
    def _build_context(self, search_results: List[Dict]) -> str:
        """Build context string from search results."""
        if not search_results:
            return "No relevant information found in the knowledge base."
        
        context_parts = []
        for i, result in enumerate(search_results, 1):
            context_parts.append(
                f"[Source {i}] ({result['metadata'].get('tax_year', 'N/A')}) "
                f"{result['content']}"
            )
        
        return "\n\n".join(context_parts)
    
    def _generate_answer(
        self, 
        question: str, 
        context: str, 
        search_results: List[Dict]
    ) -> str:
        """
        Generate answer from context.
        In production, this would call an LLM API.
        For now, it uses template-based generation with keyword extraction.
        """
        question_lower = question.lower()
        
        # Check for calculation queries
        if any(keyword in question_lower for keyword in ['calculate', 'compute', 'how much tax']):
            return self._handle_calculation_query(question, context, search_results)
        
        # Check for ETI queries
        if any(keyword in question_lower for keyword in ['eti', 'employment tax incentive', 'young worker']):
            return self._handle_eti_query(question, context)
        
        # Check for threshold queries
        if any(keyword in question_lower for keyword in ['threshold', 'not liable', 'exempt']):
            return self._handle_threshold_query(question, context)
        
        # Check for rebate queries
        if any(keyword in question_lower for keyword in ['rebate', 'credit']):
            return self._handle_rebate_query(question, context)
        
        # General query
        prompt = self.prompts['general'].format(context=context, question=question)
        return self._generate_fallback_answer(prompt, question, search_results)
    
    def _handle_calculation_query(
        self, 
        question: str, 
        context: str, 
        search_results: List[Dict]
    ) -> str:
        """Handle tax calculation queries."""
        # Extract income if mentioned
        income_match = re.search(r'R?([\d\s,]+)', question)
        income = 0
        if income_match:
            cleaned = re.sub(r'[^\d]', '', income_match.group(1))
            income = int(cleaned) if cleaned else 0
        
        # Extract tax year
        tax_year_match = re.search(r'(20\d{2})', question)
        tax_year = tax_year_match.group(1) if tax_year_match else "2025"
        
        # Get brackets from context
        brackets = self._extract_brackets(context)
        
        if brackets and income > 0:
            return self._calculate_tax_brackets(income, brackets, tax_year)
        
        prompt = self.prompts['bracket_calc'].format(
            income=income if income > 0 else 0,
            tax_year=tax_year,
            age_category='primary',
            context=context
        )
        return self._generate_fallback_answer(prompt, question, search_results)
    
    def _handle_eti_query(self, question: str, context: str) -> str:
        """Handle ETI-related queries."""
        prompt = self.prompts['eti'].format(context=context, question=question)
        return self._generate_fallback_answer(prompt, question, [])
    
    def _handle_threshold_query(self, question: str, context: str) -> str:
        """Handle tax threshold queries."""
        # Try to extract threshold info
        threshold_match = re.search(r'R([\d,]+)', context)
        if threshold_match:
            threshold = int(re.sub(r'[^\d]', '', threshold_match.group(1)))
            return f"Based on the tax tables, the tax threshold for the applicable age category is R{threshold:,}. Employees earning below this amount are generally not liable for income tax."
        
        return self._generate_fallback_answer(
            self.prompts['general'].format(context=context, question=question),
            question, []
        )
    
    def _handle_rebate_query(self, question: str, context: str) -> str:
        """Handle rebate queries."""
        # Extract rebate amounts from context
        rebates = re.findall(r'Primary Rebate.*?: R([\d,]+)', context)
        secondary = re.findall(r'Secondary Rebate.*?: R([\d,]+)', context)
        tertiary = re.findall(r'Tertiary Rebate.*?: R([\d,]+)', context)
        
        if rebates or secondary or tertiary:
            lines = ["Based on the tax tables, the following rebates apply:"]
            if rebates:
                rebate_val = rebates[0].replace(',', '')
                lines.append(f"- Primary Rebate (under 65): R{int(rebate_val):,}")
            if secondary:
                sec_val = secondary[0].replace(',', '')
                lines.append(f"- Secondary Rebate (age 65-74): R{int(sec_val):,}")
            if tertiary:
                ter_val = tertiary[0].replace(',', '')
                lines.append(f"- Tertiary Rebate (age 75+): R{int(ter_val):,}")
            return "\n".join(lines)
        
        return self._generate_fallback_answer(
            self.prompts['general'].format(context=context, question=question),
            question, []
        )
    
    def _extract_brackets(self, context: str) -> List[Dict]:
        """Extract tax brackets from context string."""
        brackets = []
        # Simple pattern matching for bracket info
        pattern = r'Taxable income above R([\d,]+) up to R([\d,]+).*?Rate (\d+)%'
        matches = re.findall(pattern, context)
        
        for match in matches:
            brackets.append({
                'above': int(match[0].replace(',', '')),
                'below': int(match[1].replace(',', '')),
                'rate': int(match[2]) / 100
            })
        
        return brackets
    
    def _calculate_tax_brackets(
        self, 
        income: int, 
        brackets: List[Dict],
        tax_year: str
    ) -> str:
        """Calculate tax using brackets."""
        if not brackets:
            return "Tax bracket information not available."
        
        lines = [f"TAX CALCULATION FOR TAX YEAR {tax_year}", f"Annual Taxable Income: R{income:,}"]
        total_tax = 0
        remaining_income = income
        
        for bracket in brackets:
            above = bracket['above']
            below = bracket['below']
            rate = bracket['rate']
            
            if remaining_income > above:
                taxable_in_bracket = min(remaining_income, below) - above
                if taxable_in_bracket > 0:
                    tax_in_bracket = taxable_in_bracket * rate
                    total_tax += tax_in_bracket
                    lines.append(
                        f"- R{above:,} to R{below:,}: R{taxable_in_bracket:,} × {rate*100:.0f}% = R{tax_in_bracket:,.0f}"
                    )
        
        if total_tax > 0:
            lines.append(f"\nEstimated PAYE: R{total_tax:,.0f}")
            lines.append(f"Monthly deduction: R{total_tax/12:,.0f}")
        
        return "\n".join(lines)
    
    def _generate_fallback_answer(
        self, 
        prompt: str, 
        question: str, 
        search_results: List[Dict]
    ) -> str:
        """
        Generate answer when LLM is not available.
        Uses keyword extraction and template filling.
        """
        # Extract key terms from question
        question_lower = question.lower()
        
        # Build answer from most relevant result
        if search_results:
            primary_result = search_results[0]
            content = primary_result['content']
            tax_year = primary_result['metadata'].get('tax_year', 'current')
            category = primary_result['metadata'].get('category', 'general')
            
            if 'bracket' in category:
                return self._summarize_brackets(content, tax_year)
            elif 'threshold' in category:
                return self._summarize_threshold(content, tax_year)
            elif 'rebate' in category:
                return self._summarize_rebate(content, tax_year)
            elif 'uif' in category:
                return self._summarize_uif(content, tax_year)
            elif 'eti' in category:
                return self._summarize_eti(content, tax_year)
            else:
                return f"Based on {tax_year} tax rules:\n\n{content[:500]}"
        
        return (
            "I need more specific information to answer your question accurately. "
            "Please provide details such as:\n"
            "- The employee's annual taxable income\n"
            "- The tax year (e.g., 2024/2025)\n"
            "- The employee's age category\n"
            "- The specific tax topic you're asking about (brackets, rebates, UIF, etc.)"
        )
    
    def _summarize_brackets(self, content: str, tax_year: str) -> str:
        """Summarize tax brackets."""
        return f"TAX BRACKETS FOR {tax_year}:\n\n{content}"
    
    def _summarize_threshold(self, content: str, tax_year: str) -> str:
        """Summarize tax thresholds."""
        return f"TAX THRESHOLDS FOR {tax_year}:\n\n{content}"
    
    def _summarize_rebate(self, content: str, tax_year: str) -> str:
        """Summarize tax rebates."""
        return f"TAX REBATES FOR {tax_year}:\n\n{content}"
    
    def _summarize_uif(self, content: str, tax_year: str) -> str:
        """Summarize UIF configuration."""
        return f"UIF CONFIGURATION FOR {tax_year}:\n\n{content}"
    
    def _summarize_eti(self, content: str, tax_year: str) -> str:
        """Summarize ETI information."""
        return f"EMPLOYMENT TAX INCENTIVE (ETI) FOR {tax_year}:\n\n{content}"
    
    def get_categories(self) -> List[str]:
        """Get list of available categories in the knowledge base."""
        categories = set()
        for doc in self.vector_store.documents.values():
            cat = doc.metadata.get('category')
            if cat:
                categories.add(cat)
        return sorted(list(categories))
    
    def get_tax_years(self) -> List[str]:
        """Get list of tax years in the knowledge base."""
        years = set()
        for doc in self.vector_store.documents.values():
            year = doc.metadata.get('tax_year')
            if year:
                years.add(str(year))
        return sorted(list(years))