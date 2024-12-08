import requests
import networkx as nx
from pyvis.network import Network
import json
from typing import List, Dict

class AdvancedResearchKnowledgeGraph:
    def __init__(self, semantic_scholar_api_key=None):
        """
        Advanced Research Knowledge Graph Constructor
        """
        self.semantic_scholar_base_url = "https://api.semanticscholar.org/graph/v1"
        self.api_key = semantic_scholar_api_key

    def fetch_paper_details(self, paper_id):
        """
        Fetch comprehensive details for a specific paper
        """
        details_url = f"{self.semantic_scholar_base_url}/paper/{paper_id}"
        try:
            response = requests.get(details_url, 
                                    params={"fields": "title,abstract,url,citations,references,authors"})
            return response.json()
        except Exception as e:
            print(f"Error fetching paper details: {e}")
            return None

    def create_comprehensive_knowledge_graph(self, initial_query):
        """
        Create an extensive, interconnected knowledge graph
        """
        # Search initial papers
        search_results = self._search_papers(initial_query)
        
        # Create NetworkX graph
        G = nx.DiGraph()
        
        # Process each paper
        for paper in search_results:
            self._process_paper_connections(G, paper)
        
        return G

    def _search_papers(self, query, limit=20):
        """
        Search for research papers
        """
        search_url = f"{self.semantic_scholar_base_url}/paper/search"
        params = {
            "query": query,
            "limit": limit,
            "fields": "paperId,title,abstract,year,authors,citations"
        }
        
        try:
            response = requests.get(search_url, params=params)
            return response.json().get('data', [])
        except Exception as e:
            print(f"Search error: {e}")
            return []

    def _process_paper_connections(self, G, paper):
        """
        Process paper connections and add to graph
        """
        paper_title = paper.get('title', 'Untitled')
        
        # Add paper node
        G.add_node(paper_title, 
                   type='paper', 
                   paper_id=paper.get('paperId'),
                   year=paper.get('year'),
                   abstract=paper.get('abstract', ''))
        
        # Add author connections
        for author in paper.get('authors', []):
            author_name = author.get('name', 'Unknown')
            G.add_node(author_name, type='author')
            G.add_edge(author_name, paper_title)
        
        return G

    def visualize_interactive_knowledge_graph(self, G):
        """
        Create an interactive, visually rich knowledge graph
        """
        net = Network(height='750px', width='100%', 
                      bgcolor='#222222', 
                      font_color='white')
        
        # Customize node and edge styles
        net.barnes_hut(gravity=-2000, 
                       central_gravity=0.3, 
                       spring_length=200, 
                       spring_strength=0.01)
        
        # Add nodes with rich metadata
        for node in G.nodes(data=True):
            node_title, node_data = node
            
            if node_data.get('type') == 'paper':
                # Papers have detailed tooltips
                net.add_node(node_title, 
                             label=node_title[:50] + '...' if len(node_title) > 50 else node_title,
                             title=f"""
                             <b>Title:</b> {node_title}<br>
                             <b>Year:</b> {node_data.get('year', 'N/A')}<br>
                             <b>Abstract:</b> {node_data.get('abstract', 'No abstract')}...<br>
                             """,
                             color='#FF6B6B',  # Vibrant red for papers
                             size=20)
            else:
                # Authors in a different color
                net.add_node(node_title, 
                             label=node_title, 
                             color='#4ECDC4',  # Teal for authors
                             size=15)
        
        # Add edges
        for edge in G.edges():
            net.add_edge(edge[0], edge[1], 
                         color='#A8DADC',  # Light blue for connections
                         width=2)
        
        # Save and show interactive graph
        net.show_buttons(filter_=['physics'])
        net.save_graph("research_knowledge_graph.html")
        net.show("research_knowledge_graph.html")

    def generate_citation_network(self, paper_title):
        """
        Create a detailed citation network for a specific paper
        """
        # Find paper by title and get its ID
        papers = self._search_papers(paper_title)
        if not papers:
            return None
        
        paper_id = papers[0].get('paperId')
        
        # Fetch citations and references
        details = self.fetch_paper_details(paper_id)
        
        # Create citation graph
        citation_graph = nx.DiGraph()
        
        # Add main paper
        citation_graph.add_node(paper_title, type='main_paper')
        
        # Add references
        for ref in details.get('references', []):
            ref_title = ref.get('title', 'Untitled Reference')
            citation_graph.add_node(ref_title, type='reference')
            citation_graph.add_edge(ref_title, paper_title)
        
        # Add citations
        for cite in details.get('citations', []):
            cite_title = cite.get('title', 'Untitled Citation')
            citation_graph.add_node(cite_title, type='citation')
            citation_graph.add_edge(paper_title, cite_title)
        
        return citation_graph

def main():
    # Initialize knowledge graph explorer
    explorer = AdvancedResearchKnowledgeGraph()
    
    # Get research topic
    topic = input("Enter research topic: ")
    
    # Create comprehensive knowledge graph
    knowledge_graph = explorer.create_comprehensive_knowledge_graph(topic)
    
    # Visualize interactive graph
    explorer.visualize_interactive_knowledge_graph(knowledge_graph)
    
    # Optional: Explore citation network for a specific paper
    specific_paper = input("Enter a specific paper title for citation network: ")
    citation_network = explorer.generate_citation_network(specific_paper)
    
    if citation_network:
        explorer.visualize_interactive_knowledge_graph(citation_network)

if __name__ == "__main__":
    main()