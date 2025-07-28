#!/usr/bin/env python3
"""
Minimal Multi-Collection PDF Analysis for Adobe India Hackathon 2025
Works without external downloads and focuses on core functionality
"""

import os
import json
import re
import time
from pathlib import Path
from typing import List, Dict, Any, Tuple
from datetime import datetime
import fitz  # PyMuPDF

class MinimalCollectionProcessor:
    def __init__(self):
        # Basic stop words without NLTK
        self.stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the', 
            'to', 'was', 'will', 'with', 'the', 'this', 'but', 'they', 'have', 
            'had', 'what', 'said', 'each', 'which', 'she', 'do', 'how', 'their', 
            'if', 'up', 'out', 'many', 'then', 'them', 'these', 'so', 'some', 
            'her', 'would', 'make', 'like', 'into', 'him', 'time', 'two', 'more', 
            'go', 'no', 'way', 'could', 'my', 'than', 'first', 'been', 'call', 
            'who', 'its', 'now', 'find', 'long', 'down', 'day', 'did', 'get', 
            'come', 'made', 'may', 'part'
        }
        
        # Persona-specific keywords and patterns
        self.persona_keywords = {
            "Travel Planner": [
                "travel", "trip", "vacation", "hotel", "restaurant", "attraction", 
                "itinerary", "booking", "reservation", "transport", "accommodation",
                "sightseeing", "tour", "guide", "map", "location", "city", "region",
                "culture", "cuisine", "activities", "entertainment", "budget", "cost",
                "france", "south", "mediterranean", "coast", "beach", "wine", "food"
            ],
            "HR Professional": [
                "form", "document", "signature", "compliance", "onboarding", 
                "employee", "hr", "human resources", "policy", "procedure",
                "fillable", "editable", "template", "workflow", "approval",
                "digital", "electronic", "automation", "process", "management",
                "acrobat", "pdf", "fill", "sign", "export", "share", "edit"
            ],
            "Food Contractor": [
                "recipe", "cooking", "food", "ingredient", "meal", "dish",
                "vegetarian", "buffet", "catering", "menu", "preparation",
                "kitchen", "chef", "culinary", "dining", "service", "corporate",
                "event", "gathering", "party", "celebration", "dietary", "nutrition",
                "breakfast", "lunch", "dinner", "main", "side", "appetizer"
            ]
        }
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract all text from a PDF file."""
        try:
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except Exception as e:
            print(f"Error extracting text from {pdf_path}: {e}")
            return ""
    
    def extract_sections_from_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extract sections with page numbers from PDF."""
        sections = []
        
        try:
            doc = fitz.open(pdf_path)
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                blocks = page.get_text("dict")["blocks"]
                
                current_section = {
                    "text": "",
                    "page": page_num + 1,
                    "font_sizes": [],
                    "is_heading": False
                }
                
                for block in blocks:
                    if "lines" in block:
                        for line in block["lines"]:
                            for span in line["spans"]:
                                text = span["text"].strip()
                                if text:
                                    font_size = span["size"]
                                    is_bold = bool(span["flags"] & 2**4)
                                    
                                    # Check if this looks like a heading
                                    if (font_size > 14 or is_bold or 
                                        re.match(r'^[A-Z][A-Z\s]{2,}$', text) or
                                        re.match(r'^\d+\.\s+[A-Z]', text)):
                                        
                                        # Save previous section if it exists
                                        if current_section["text"].strip():
                                            sections.append(current_section.copy())
                                        
                                        # Start new section
                                        current_section = {
                                            "text": text,
                                            "page": page_num + 1,
                                            "font_sizes": [font_size],
                                            "is_heading": True
                                        }
                                    else:
                                        # Add to current section
                                        if current_section["text"]:
                                            current_section["text"] += " " + text
                                        else:
                                            current_section["text"] = text
                                        current_section["font_sizes"].append(font_size)
                
                # Add the last section of the page
                if current_section["text"].strip():
                    sections.append(current_section.copy())
            
            doc.close()
            
        except Exception as e:
            print(f"Error extracting sections from {pdf_path}: {e}")
        
        return sections
    
    def simple_tokenize(self, text: str) -> List[str]:
        """Simple tokenization without NLTK."""
        # Split by whitespace and remove punctuation
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        return [word for word in words if word not in self.stop_words]
    
    def calculate_persona_relevance(self, text: str, persona: str) -> float:
        """Calculate how relevant a text section is to a specific persona."""
        if not text or not persona:
            return 0.0
        
        # Get persona keywords
        keywords = self.persona_keywords.get(persona, [])
        if not keywords:
            return 0.0
        
        # Simple keyword matching
        text_lower = text.lower()
        keyword_matches = 0
        for keyword in keywords:
            if keyword.lower() in text_lower:
                keyword_matches += 1
        
        # Calculate relevance score
        relevance = keyword_matches / len(keywords) if keywords else 0.0
        
        # Boost score for longer, more detailed sections
        if len(text) > 100:
            relevance *= 1.2
        
        return min(relevance, 1.0)
    
    def rank_sections_by_importance(self, sections: List[Dict[str, Any]], persona: str, task: str) -> List[Dict[str, Any]]:
        """Rank sections by importance for the given persona and task."""
        ranked_sections = []
        
        for section in sections:
            text = section.get("text", "")
            if not text.strip():
                continue
            
            # Calculate various importance factors
            persona_relevance = self.calculate_persona_relevance(text, persona)
            task_relevance = self.calculate_persona_relevance(text, task)
            
            # Length factor (longer sections might be more important)
            length_factor = min(len(text) / 1000, 1.0)
            
            # Heading factor
            heading_factor = 1.5 if section.get("is_heading", False) else 1.0
            
            # Font size factor
            font_sizes = section.get("font_sizes", [])
            if font_sizes:
                avg_font_size = sum(font_sizes) / len(font_sizes)
                font_factor = min(avg_font_size / 12, 2.0)
            else:
                font_factor = 1.0
            
            # Calculate overall importance score
            importance_score = (
                persona_relevance * 0.4 +
                task_relevance * 0.3 +
                length_factor * 0.2 +
                heading_factor * 0.1
            ) * font_factor
            
            ranked_sections.append({
                **section,
                "importance_score": importance_score,
                "persona_relevance": persona_relevance,
                "task_relevance": task_relevance
            })
        
        # Sort by importance score
        ranked_sections.sort(key=lambda x: x["importance_score"], reverse=True)
        
        return ranked_sections
    
    def refine_text_for_subsection(self, text: str) -> str:
        """Refine and clean text for subsection analysis."""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove page numbers and headers
        text = re.sub(r'\b\d+\s*$', '', text)
        
        # Limit length for readability
        if len(text) > 2000:
            # Simple sentence splitting
            sentences = re.split(r'[.!?]+', text)
            refined_text = ""
            for sentence in sentences:
                if len(refined_text + sentence) < 2000:
                    refined_text += sentence + ". "
                else:
                    break
            text = refined_text.strip()
        
        return text
    
    def process_collection(self, collection_path: str) -> Dict[str, Any]:
        """Process a single collection and return analysis results."""
        collection_path = Path(collection_path)
        
        # Read input configuration
        input_file = collection_path / "challenge1b_input.json"
        if not input_file.exists():
            return {"error": f"Input file not found: {input_file}"}
        
        with open(input_file, 'r', encoding='utf-8') as f:
            input_config = json.load(f)
        
        # Extract configuration
        challenge_id = input_config.get("challenge_info", {}).get("challenge_id", "")
        documents = input_config.get("documents", [])
        persona = input_config.get("persona", {}).get("role", "")
        task = input_config.get("job_to_be_done", {}).get("task", "")
        
        print(f"Processing collection: {challenge_id}")
        print(f"Persona: {persona}")
        print(f"Task: {task}")
        print(f"Documents: {len(documents)}")
        
        # Process all documents
        all_sections = []
        document_texts = {}
        
        for doc_info in documents:
            filename = doc_info.get("filename", "")
            pdf_path = collection_path / "PDFs" / filename
            
            if pdf_path.exists():
                print(f"Processing document: {filename}")
                
                # Extract text and sections
                full_text = self.extract_text_from_pdf(str(pdf_path))
                sections = self.extract_sections_from_pdf(str(pdf_path))
                
                document_texts[filename] = full_text
                
                # Add document info to sections
                for section in sections:
                    section["document"] = filename
                    all_sections.append(section)
        
        # Rank sections by importance
        ranked_sections = self.rank_sections_by_importance(all_sections, persona, task)
        
        # Select top sections for extracted_sections
        top_sections = ranked_sections[:10]  # Top 10 most important sections
        
        extracted_sections = []
        for i, section in enumerate(top_sections):
            extracted_sections.append({
                "document": section["document"],
                "section_title": section["text"][:200] + "..." if len(section["text"]) > 200 else section["text"],
                "importance_rank": i + 1,
                "page_number": section["page"]
            })
        
        # Create subsection analysis
        subsection_analysis = []
        for section in ranked_sections[:15]:  # Top 15 for detailed analysis
            refined_text = self.refine_text_for_subsection(section["text"])
            if refined_text:
                subsection_analysis.append({
                    "document": section["document"],
                    "refined_text": refined_text,
                    "page_number": section["page"]
                })
        
        # Create output
        output = {
            "metadata": {
                "input_documents": [doc.get("filename", "") for doc in documents],
                "persona": persona,
                "job_to_be_done": task,
                "processing_timestamp": datetime.now().isoformat()
            },
            "extracted_sections": extracted_sections,
            "subsection_analysis": subsection_analysis
        }
        
        return output
    
    def process_all_collections(self, base_path: str = "."):
        """Process all collections in the base path."""
        base_path = Path(base_path)
        
        # Find all collection directories
        collections = [d for d in base_path.iterdir() if d.is_dir() and d.name.startswith("Collection")]
        
        print(f"Found {len(collections)} collections to process")
        
        for collection_path in collections:
            print(f"\n{'='*50}")
            print(f"Processing {collection_path.name}")
            print(f"{'='*50}")
            
            try:
                # Process the collection
                result = self.process_collection(collection_path)
                
                # Save output
                output_file = collection_path / "challenge1b_output.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                
                print(f"✓ Saved results to {output_file}")
                print(f"  Extracted sections: {len(result.get('extracted_sections', []))}")
                print(f"  Subsection analysis: {len(result.get('subsection_analysis', []))}")
                
            except Exception as e:
                print(f"✗ Error processing {collection_path.name}: {e}")

def main():
    """Main function to process all collections."""
    print("🚀 Adobe India Hackathon 2025 - Multi-Collection PDF Analysis")
    print("=" * 60)
    
    # Initialize processor
    processor = MinimalCollectionProcessor()
    
    # Process all collections
    processor.process_all_collections()
    
    print("\n✅ Multi-collection analysis completed!")

if __name__ == "__main__":
    main() 