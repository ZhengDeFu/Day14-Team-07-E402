from typing import List, Dict

class DocumentChunker:
    """
    Chunking strategy để chia documents thành smaller, more relevant pieces.
    Giúp improve retrieval precision và reduce noise.
    """
    
    def __init__(self, chunk_size: int = 500, overlap: int = 100):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_by_size(self, text: str, doc_id: str) -> List[Dict]:
        """
        Chia document thành chunks dựa trên size.
        """
        chunks = []
        start = 0
        chunk_num = 0
        
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            chunk_text = text[start:end]
            
            chunks.append({
                "id": f"{doc_id}_chunk_{chunk_num}",
                "content": chunk_text,
                "start": start,
                "end": end,
                "original_doc": doc_id
            })
            
            start = end - self.overlap
            chunk_num += 1
        
        return chunks
    
    def chunk_by_sentences(self, text: str, doc_id: str, sentences_per_chunk: int = 5) -> List[Dict]:
        """
        Chia document thành chunks dựa trên sentences.
        """
        import re
        
        # Split by sentence
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        chunk_num = 0
        
        for i in range(0, len(sentences), sentences_per_chunk):
            chunk_sentences = sentences[i:i + sentences_per_chunk]
            chunk_text = " ".join(chunk_sentences)
            
            if chunk_text.strip():
                chunks.append({
                    "id": f"{doc_id}_chunk_{chunk_num}",
                    "content": chunk_text,
                    "sentence_range": (i, i + len(chunk_sentences)),
                    "original_doc": doc_id
                })
                chunk_num += 1
        
        return chunks
    
    def chunk_by_sections(self, text: str, doc_id: str) -> List[Dict]:
        """
        Chia document thành chunks dựa trên sections (headings).
        """
        import re
        
        # Split by headings (# ## ###)
        sections = re.split(r'^#+\s+', text, flags=re.MULTILINE)
        chunks = []
        chunk_num = 0
        
        for section in sections:
            if section.strip():
                chunks.append({
                    "id": f"{doc_id}_chunk_{chunk_num}",
                    "content": section.strip(),
                    "original_doc": doc_id
                })
                chunk_num += 1
        
        return chunks
    
    def chunk_smart(self, text: str, doc_id: str) -> List[Dict]:
        """
        Smart chunking: combine size-based and section-based.
        """
        # First try section-based
        section_chunks = self.chunk_by_sections(text, doc_id)
        
        # If sections are too large, further chunk by size
        final_chunks = []
        chunk_num = 0
        
        for section_chunk in section_chunks:
            if len(section_chunk["content"]) > self.chunk_size:
                # Further chunk by size
                sub_chunks = self.chunk_by_size(section_chunk["content"], 
                                               f"{doc_id}_section_{chunk_num}")
                final_chunks.extend(sub_chunks)
            else:
                section_chunk["id"] = f"{doc_id}_chunk_{chunk_num}"
                final_chunks.append(section_chunk)
            
            chunk_num += 1
        
        return final_chunks

class ChunkingStrategy:
    """
    Strategy pattern cho different chunking approaches.
    """
    
    STRATEGIES = {
        "size": "chunk_by_size",
        "sentences": "chunk_by_sentences",
        "sections": "chunk_by_sections",
        "smart": "chunk_smart"
    }
    
    def __init__(self, strategy: str = "smart"):
        self.strategy = strategy
        self.chunker = DocumentChunker()
    
    def chunk(self, text: str, doc_id: str) -> List[Dict]:
        """Chunk document using selected strategy."""
        method_name = self.STRATEGIES.get(self.strategy, "chunk_smart")
        method = getattr(self.chunker, method_name)
        return method(text, doc_id)

if __name__ == "__main__":
    chunker = DocumentChunker()
    
    text = """
    # VF8 User Manual
    
    ## Chapter 1: Introduction
    VF8 is an electric SUV. It has 5 seats.
    
    ## Chapter 2: Specifications
    - Battery: 82 kWh
    - Range: 500 km
    - Charging time: 30 minutes
    """
    
    chunks = chunker.chunk_smart(text, "vf8_manual.md")
    for chunk in chunks:
        print(f"Chunk {chunk['id']}: {chunk['content'][:50]}...")
