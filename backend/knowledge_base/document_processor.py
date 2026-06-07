"""
Document Processor for loading and chunking tax documents.
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class Chunk:
    """Represents a chunk of processed content."""
    content: str
    metadata: Dict[str, Any]
    chunk_id: Optional[str] = None


class DocumentProcessor:
    """
    Processes tax documents into chunks suitable for RAG.
    Handles various formats and creates meaningful chunks.
    """
    
    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        """
        Initialize the document processor.
        
        Args:
            chunk_size: Target size of each chunk in characters
            overlap: Overlap between chunks in characters
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def process_json_tax_file(self, file_path: str) -> List[Chunk]:
        """
        Process a JSON tax data file into chunks.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            List of Chunk objects
        """
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        chunks = []
        tax_year = data.get('tax_year', 'unknown')
        
        # Process income tax brackets
        if 'income_tax_brackets' in data:
            brackets_content = self._format_brackets(
                data['income_tax_brackets'], 
                tax_year
            )
            chunks.append(Chunk(
                content=brackets_content,
                metadata={
                    'source': 'tax_brackets',
                    'tax_year': tax_year,
                    'category': 'income_tax'
                }
            ))
        
        # Process tax rebates
        if 'tax_rebates' in data:
            rebates_content = self._format_rebates(
                data['tax_rebates'],
                tax_year
            )
            chunks.append(Chunk(
                content=rebates_content,
                metadata={
                    'source': 'tax_rebates',
                    'tax_year': tax_year,
                    'category': 'rebates'
                }
            ))
        
        # Process tax thresholds
        if 'tax_thresholds' in data:
            thresholds_content = self._format_thresholds(
                data['tax_thresholds'],
                tax_year
            )
            chunks.append(Chunk(
                content=thresholds_content,
                metadata={
                    'source': 'tax_thresholds',
                    'tax_year': tax_year,
                    'category': 'thresholds'
                }
            ))
        
        # Process medical credits
        if 'medical_scheme_credits' in data:
            medical_content = self._format_medical_credits(
                data['medical_scheme_credits'],
                tax_year
            )
            chunks.append(Chunk(
                content=medical_content,
                metadata={
                    'source': 'medical_credits',
                    'tax_year': tax_year,
                    'category': 'medical_credits'
                }
            ))
        
        # Process UIF config
        if 'uif' in data:
            uif_content = self._format_uif(data['uif'], tax_year)
            chunks.append(Chunk(
                content=uif_content,
                metadata={
                    'source': 'uif_config',
                    'tax_year': tax_year,
                    'category': 'uif'
                }
            ))
        
        # Process SDL config
        if 'sdl' in data:
            sdl_content = self._format_sdl(data['sdl'], tax_year)
            chunks.append(Chunk(
                content=sdl_content,
                metadata={
                    'source': 'sdl_config',
                    'tax_year': tax_year,
                    'category': 'sdl'
                }
            ))
        
        # Process ETI config
        if 'eti' in data:
            eti_content = self._format_eti(data['eti'], tax_year)
            chunks.append(Chunk(
                content=eti_content,
                metadata={
                    'source': 'eti_config',
                    'tax_year': tax_year,
                    'category': 'eti'
                }
            ))
        
        return chunks
    
    def _format_brackets(self, brackets: List[Dict], tax_year: str) -> str:
        """Format tax brackets into readable text."""
        lines = [
            f"INCOME TAX BRACKETS FOR TAX YEAR {tax_year}:",
            "The following brackets determine how much income tax an employee pays based on their annual taxable income:",
        ]
        
        for bracket in brackets:
            threshold = bracket.get('threshold', 0)
            rate = bracket.get('rate', 0)
            base = bracket.get('base_amount', 0)
            above = bracket.get('above', 0)
            
            lines.append(
                f"- Taxable income above R{above:,.0f} up to R{above + (threshold - above):,.0f}: "
                f"Rate {rate*100:.0f}%, Base tax R{base:,.0f}"
            )
        
        return "\n".join(lines)
    
    def _format_rebates(self, rebates: Dict, tax_year: str) -> str:
        """Format tax rebates into readable text."""
        lines = [
            f"TAX REBATES FOR TAX YEAR {tax_year}:",
            "Tax rebates reduce the amount of tax owed:",
        ]
        
        rebate_types = {
            'primary': 'Primary Rebate (under 65)',
            'secondary': 'Secondary Rebate (age 65 to 74)',
            'tertiary': 'Tertiary Rebate (age 75+)'
        }
        
        for rebate_type, label in rebate_types.items():
            if rebate_type in rebates:
                lines.append(f"- {label}: R{rebates[rebate_type]:,.0f}")
        
        return "\n".join(lines)
    
    def _format_thresholds(self, thresholds: Dict, tax_year: str) -> str:
        """Format tax thresholds into readable text."""
        lines = [
            f"TAX THRESHOLDS FOR TAX YEAR {tax_year}:",
            "Employees earning below these thresholds are not liable for income tax:",
        ]
        
        if 'under_65' in thresholds:
            lines.append(f"- Under 65 years: R{thresholds['under_65']:,.0f}")
        if 'age_65_to_74' in thresholds:
            lines.append(f"- Age 65 to 74: R{thresholds['age_65_to_74']:,.0f}")
        if 'age_75_plus' in thresholds:
            lines.append(f"- Age 75 and over: R{thresholds['age_75_plus']:,.0f}")
        
        return "\n".join(lines)
    
    def _format_medical_credits(self, credits: Dict, tax_year: str) -> str:
        """Format medical scheme credits into readable text."""
        lines = [
            f"MEDICAL SCHEME TAX CREDITS FOR TAX YEAR {tax_year}:",
            "These credits reduce taxable income:",
        ]
        
        if 'main_member' in credits:
            lines.append(f"- Main member: R{credits['main_member']:,.0f} per month")
        if 'first_dependent' in credits:
            lines.append(f"- First dependent: R{credits['first_dependent']:,.0f} per month")
        if 'additional_dependent' in credits:
            lines.append(f"- Each additional dependent: R{credits['additional_dependent']:,.0f} per month")
        
        return "\n".join(lines)
    
    def _format_uif(self, uif: Dict, tax_year: str) -> str:
        """Format UIF configuration into readable text."""
        lines = [
            f"UNEMPLOYMENT INSURANCE FUND (UIF) CONFIGURATION FOR TAX YEAR {tax_year}:",
            f"- Employee contribution rate: {uif.get('employee_rate', 0)*100:.2f}%",
            f"- Employer contribution rate: {uif.get('employer_rate', 0)*100:.2f}%",
            f"- Monthly earnings cap: R{uif.get('monthly_cap', 0):,.2f}",
        ]
        
        return "\n".join(lines)
    
    def _format_sdl(self, sdl: Dict, tax_year: str) -> str:
        """Format SDL configuration into readable text."""
        lines = [
            f"SKILLS DEVELOPMENT LEVY (SDL) CONFIGURATION FOR TAX YEAR {tax_year}:",
            f"- SDL rate: {sdl.get('rate', 0)*100:.2f}%",
            f"- Annual earnings threshold: R{sdl.get('annual_threshold', 0):,.0f}",
        ]
        
        return "\n".join(lines)
    
    def _format_eti(self, eti: Dict, tax_year: str) -> str:
        """Format ETI configuration into readable text."""
        lines = [
            f"EMPLOYMENT TAX INCENTIVE (ETI) FOR TAX YEAR {tax_year}:",
            "ETI provides incentives for employing young workers:",
        ]
        
        for phase_name, phase_data in eti.items():
            lines.append(f"\n{phase_name.replace('_', ' ').upper()}:")
            if 'remuneration_brackets' in phase_data:
                for bracket in phase_data['remuneration_brackets']:
                    min_r = bracket.get('min', 0)
                    max_r = bracket.get('max', 0)
                    if 'formula' in bracket:
                        lines.append(
                            f"- Monthly remuneration R{min_r:,.0f} to R{max_r:,.0f}: "
                            f"Formula: {bracket['formula']}"
                        )
                    elif 'fixed_amount' in bracket:
                        lines.append(
                            f"- Monthly remuneration R{min_r:,.0f} to R{max_r:,.0f}: "
                            f"Fixed amount: R{bracket['fixed_amount']:,.0f}"
                        )
        
        return "\n".join(lines)
    
    def process_text(self, text: str, metadata: Dict[str, Any]) -> List[Chunk]:
        """
        Process raw text into chunks with overlap.
        
        Args:
            text: Text content to process
            metadata: Metadata to attach to chunks
            
        Returns:
            List of Chunk objects
        """
        chunks = []
        
        # Split by paragraphs first
        paragraphs = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]
        
        current_chunk = []
        current_length = 0
        
        for para in paragraphs:
            para_len = len(para)
            
            if current_length + para_len > self.chunk_size and current_chunk:
                # Save current chunk
                chunks.append(Chunk(
                    content="\n\n".join(current_chunk),
                    metadata=dict(metadata)
                ))
                
                # Start new chunk with overlap
                overlap_chars = "\n\n".join(current_chunk)[-self.overlap:] if current_chunk else ""
                current_chunk = [overlap_chars, para]
                current_length = len(overlap_chars) + para_len
            else:
                current_chunk.append(para)
                current_length += para_len
        
        # Don't forget the last chunk
        if current_chunk:
            chunks.append(Chunk(
                content="\n\n".join(current_chunk),
                metadata=dict(metadata)
            ))
        
        return chunks
    
    def process_directory(self, directory_path: str) -> List[Chunk]:
        """
        Process all JSON files in a directory.
        
        Args:
            directory_path: Path to directory containing tax data
            
        Returns:
            List of all chunks from all files
        """
        all_chunks = []
        path = Path(directory_path)
        
        for json_file in sorted(path.glob("*.json")):
            try:
                chunks = self.process_json_tax_file(str(json_file))
                all_chunks.extend(chunks)
            except Exception as e:
                print(f"Error processing {json_file}: {e}")
        
        return all_chunks