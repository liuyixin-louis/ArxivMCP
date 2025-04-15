# import requests
from typing import Any, Dict, List

import httpx
from bs4 import BeautifulSoup
from mcp.server.fastmcp import FastMCP

mcp = FastMCP('paper-search')

# Constants
API_BASE = "http://localhost:8001"
USER_AGENT = "paper-search/1.0"

async def make_api_request(url: str, params: Dict[str, Any] = None, method: str = "GET") -> Dict[str, Any] | None:
    """Make a request to the paper search API"""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json"
    }
    async with httpx.AsyncClient() as client:
        try:
            if method.upper() == "GET":
                response = await client.get(url, headers=headers, params=params, timeout=30.0)
            else:
                response = await client.post(url, headers=headers, json=params, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e}")
            return None

def format_paper(paper: Dict[str, Any]) -> str:
    """Format a paper into a readable string"""
    return f"""
Title: {paper.get('title', 'Unknown')}
Authors: {', '.join(paper.get('authors', ['Unknown']))}
ArXiv ID: {paper.get('arxiv_id', 'Unknown')}
Categories: {', '.join(paper.get('categories', ['Unknown']))}
Score: {paper.get('score', 0):.3f}
Summary: {paper.get('summary', 'No summary available')}
PDF URL: {paper.get('pdf_url', 'No URL available')}
Updated: {paper.get('updated', 'Unknown')}
BibTeX: {paper.get('bibtex', 'No BibTeX available')}
"""

@mcp.tool()
async def search_papers_local_arxiv(query: str, k: int = 5) -> str:
    """Search for academic papers based on a query text.
    Args:
        query: The search query text to find relevant papers
        k: Number of results to return (1-1000, default: 5)
    """
    url = f"{API_BASE}/direct_search"
    params = {
        "query": query,
        "k": min(k, 1000)  # Limit largest results to 1000
    }
    
    data = await make_api_request(url, params, method="POST")
    if not data:
        return "No papers found or error occurred while searching."
    
    # Format each paper and join them with separators
    papers = [format_paper(paper) for paper in data]
    return "\n---\n".join(papers)

@mcp.tool()
async def read_arxiv_latex_content(arxiv_id: str) -> str:
    """Fetch the cleaned content in latex format from an arXiv paper given its ID.
    Args:
        arxiv_id: The arXiv ID of the paper to fetch
    """
    url = f"{API_BASE}/arxiv_content"
    params = {
        "arxiv_id": arxiv_id
    }
    
    data = await make_api_request(url, params, method="POST")
    if not data:
        return f"Error: Could not retrieve content for arxiv ID {arxiv_id}."
    
    return data.get("content", "Content not available")

@mcp.tool()
async def read_arxiv_bibtex(arxiv_id: str) -> str:
    """Get the BibTeX citation for an arXiv paper.
    Args:
        arxiv_id: The arXiv ID of the paper to fetch BibTeX for
    """
    url = f"{API_BASE}/arxiv_bibtex"
    params = {
        "arxiv_id": arxiv_id
    }
    
    data = await make_api_request(url, params, method="POST")
    if not data:
        return f"Error: Could not retrieve BibTeX for arxiv ID {arxiv_id}."
    
    return data.get("bibtex", "BibTeX not available")

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')
