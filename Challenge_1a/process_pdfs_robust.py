#!/usr/bin/env python3
"""
Robust PDF Processing Solution for Adobe India Hackathon 2025
Handles edge cases and provides better error handling
"""

import os
import json
import re
import time
from pathlib import Path
from typing import List, Dict, Any, Tuple
import fitz  # PyMuPDF
from collections import defaultdict

class RobustPDFProcessor:
    def __init__(self):
        self.heading_patterns = [
            r'^[A-Z][A-Z\s]{2,}$',  # ALL CAPS headings
            r'^\d+\.\s+[A-Z]',      # Numbered headings
            r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*$',  # Title Case headings
            r'^Chapter\s+\d+',      # Chapter headings
            r'^Section\s+\d+',      # Section headings
        ]
        
    def extract_text_with_positions(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extract text with font information and positions."""
        text_blocks = []
        
        try:
            # Use PyMuPDF for detailed text extraction
            doc = fitz.open(pdf_path)
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                try:
                    blocks = page.get_text("dict")["blocks"]
                    
                    for block in blocks:
                        if "lines" in block:
                            for line in block["lines"]:
                                for span in line["spans"]:
                                    text = span["text"].strip()
                                    if text:
                                        text_blocks.append({
                                            "text": text,
                                            "page": page_num + 1,
                                            "font_size": span["size"],
                                            "font_flags": span["flags"],
                                            "bbox": span["bbox"],
                                            "is_bold": bool(span["flags"] & 2**4),
                                            "is_italic": bool(span["flags"] & 2**1)
                                        })
                except Exception as e:
                    print(f"Error processing page {page_num + 1}: {e}")
                    continue
            
            doc.close()
        except Exception as e:
            print(f"Error extracting text from {pdf_path}: {e}")
            return []
            
        return text_blocks
    
    def identify_headings(self, text_blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify headings based on font characteristics and patterns."""
        headings = []
        
        if not text_blocks:
            return headings
        
        # Group text blocks by page
        pages = defaultdict(list)
        for block in text_blocks:
            pages[block["page"]].append(block)
        
        # Analyze each page
        for page_num, page_blocks in pages.items():
            if not page_blocks:
                continue
                
            try:
                # Sort by vertical position (top to bottom)
                page_blocks.sort(key=lambda x: x.get("bbox", [0, 0, 0, 0])[1])
                
                # Find potential headings
                for i, block in enumerate(page_blocks):
                    text = block["text"]
                    font_size = block["font_size"]
                    is_bold = block["is_bold"]
                    
                    # Skip very short text or common non-headings
                    if len(text) < 3 or text.lower() in ['page', 'continued', '...']:
                        continue
                    
                    # Check if this looks like a heading
                    is_heading = False
                    level = "H3"  # Default level
                    
                    # Check font characteristics
                    if font_size > 12 or is_bold:
                        is_heading = True
                        if font_size > 16:
                            level = "H1"
                        elif font_size > 14:
                            level = "H2"
                    
                    # Check text patterns
                    for pattern in self.heading_patterns:
                        if re.match(pattern, text):
                            is_heading = True
                            if re.match(r'^[A-Z][A-Z\s]{2,}$', text):
                                level = "H1"
                            elif re.match(r'^\d+\.\s+[A-Z]', text):
                                level = "H2"
                            break
                    
                    # Check if it's the first significant text on the page
                    if i == 0 and len(text) > 5 and not text.isdigit():
                        is_heading = True
                        level = "H1"
                    
                    # Check if it's followed by body text
                    if i < len(page_blocks) - 1:
                        next_block = page_blocks[i + 1]
                        if (next_block["font_size"] < font_size and 
                            len(next_block["text"]) > 20):
                            is_heading = True
                    
                    if is_heading:
                        headings.append({
                            "level": level,
                            "text": text,
                            "page": page_num,
                            "font_size": font_size,
                            "confidence": self.calculate_heading_confidence(block, page_blocks)
                        })
            except Exception as e:
                print(f"Error processing page {page_num}: {e}")
                continue
        
        # Sort headings by page and position
        try:
            headings.sort(key=lambda x: (x["page"], x.get("bbox", [0])[1]))
        except:
            # Fallback sorting
            headings.sort(key=lambda x: x["page"])
        
        return headings
    
    def calculate_heading_confidence(self, block: Dict[str, Any], page_blocks: List[Dict[str, Any]]) -> float:
        """Calculate confidence score for heading identification."""
        confidence = 0.0
        
        try:
            # Font size bonus
            if block["font_size"] > 14:
                confidence += 0.3
            elif block["font_size"] > 12:
                confidence += 0.2
            
            # Bold text bonus
            if block["is_bold"]:
                confidence += 0.3
            
            # Pattern matching bonus
            text = block["text"]
            for pattern in self.heading_patterns:
                if re.match(pattern, text):
                    confidence += 0.2
                    break
            
            # Length bonus (not too short, not too long)
            if 3 <= len(text) <= 100:
                confidence += 0.1
            
            # Position bonus (top of page)
            if block.get("bbox"):
                y_pos = block["bbox"][1]
                page_height = max(b.get("bbox", [0, 0, 0, 0])[3] for b in page_blocks)
                if y_pos < page_height * 0.3:  # Top 30% of page
                    confidence += 0.1
        except Exception as e:
            print(f"Error calculating confidence: {e}")
        
        return min(confidence, 1.0)
    
    def extract_title(self, text_blocks: List[Dict[str, Any]], headings: List[Dict[str, Any]]) -> str:
        """Extract document title from the first significant heading or text."""
        if not text_blocks:
            return "Untitled Document"
        
        # Look for the first H1 heading
        for heading in headings:
            if heading["level"] == "H1":
                return heading["text"]
        
        # Look for the first significant text block
        for block in text_blocks:
            text = block["text"].strip()
            if (len(text) > 5 and 
                not text.isdigit() and 
                not text.lower().startswith(('page', 'continued'))):
                return text[:100]  # Limit title length
        
        return "Untitled Document"
    
    def refine_outline(self, headings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Refine and clean the outline structure."""
        refined_outline = []
        
        for heading in headings:
            try:
                # Clean the text
                text = heading["text"].strip()
                if not text:
                    continue
                
                # Skip very low confidence headings
                if heading.get("confidence", 0) < 0.3:
                    continue
                
                # Normalize level
                level = heading["level"]
                
                refined_outline.append({
                    "level": level,
                    "text": text,
                    "page": heading["page"]
                })
            except Exception as e:
                print(f"Error refining heading: {e}")
                continue
        
        return refined_outline
    
    def process_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Process a single PDF and return structured data."""
        start_time = time.time()
        
        try:
            # Extract text with positioning information
            text_blocks = self.extract_text_with_positions(pdf_path)
            
            if not text_blocks:
                return {
                    "title": "Error: Could not extract text",
                    "outline": []
                }
            
            # Identify headings
            headings = self.identify_headings(text_blocks)
            
            # Extract title
            title = self.extract_title(text_blocks, headings)
            
            # Refine outline
            outline = self.refine_outline(headings)
            
            processing_time = time.time() - start_time
            print(f"Processed {pdf_path} in {processing_time:.2f} seconds")
            
            return {
                "title": title,
                "outline": outline
            }
        except Exception as e:
            print(f"Error processing {pdf_path}: {e}")
            return {
                "title": f"Error processing {Path(pdf_path).name}",
                "outline": []
            }

def process_pdfs():
    """Main function to process all PDFs in the input directory."""
    print("Starting PDF processing...")
    
    # Initialize processor
    processor = RobustPDFProcessor()
    
    # Get input and output directories (local paths)
    input_dir = Path("sample_dataset/pdfs")
    output_dir = Path("sample_dataset/outputs")
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Get all PDF files
    pdf_files = list(input_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("No PDF files found in input directory")
        return
    
    print(f"Found {len(pdf_files)} PDF files to process")
    
    # Process each PDF
    for pdf_file in pdf_files:
        try:
            print(f"Processing {pdf_file.name}...")
            
            # Process the PDF
            result = processor.process_pdf(str(pdf_file))
            
            # Create output JSON file
            output_file = output_dir / f"{pdf_file.stem}.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"✓ Processed {pdf_file.name} -> {output_file.name}")
            print(f"  Title: {result['title']}")
            print(f"  Outline sections: {len(result['outline'])}")
            
        except Exception as e:
            print(f"✗ Error processing {pdf_file.name}: {e}")
            # Create error output
            error_result = {
                "title": f"Error processing {pdf_file.name}",
                "outline": []
            }
            output_file = output_dir / f"{pdf_file.stem}.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(error_result, f, indent=2, ensure_ascii=False)
    
    print("PDF processing completed!")

if __name__ == "__main__":
    process_pdfs() 