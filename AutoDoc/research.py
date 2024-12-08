import requests
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from scholarly import scholarly
from transformers import pipeline, BartForConditionalGeneration, BartTokenizer
import torch
from functools import lru_cache

nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

class ResearchAssistant:
    def __init__(self):
        self.model_name = "facebook/bart-large-cnn"
        self.tokenizer = BartTokenizer.from_pretrained(self.model_name)
        self.model = BartForConditionalGeneration.from_pretrained(self.model_name)
        self.summarizer = pipeline("summarization", model=self.model, tokenizer=self.tokenizer, 
                                   max_length=150, min_length=50, length_penalty=2.0, num_beams=4, 
                                   device=0 if torch.cuda.is_available() else -1)

    @lru_cache(maxsize=100)
    def search_papers(self, query, num_results=5):
        search_query = scholarly.search_pubs(query)
        papers = []
        for i in range(num_results):
            try:
                paper = next(search_query)
                bib = paper['bib']
                papers.append({
                    'title': bib['title'],
                    'author': bib['author'],
                    'year': bib['pub_year'],
                    'abstract': bib['abstract'] if 'abstract' in bib else "N/A",
                    'url': paper['url_scholarbib']
                })
            except StopIteration:
                break
        return tuple(papers)  # Convert to tuple for caching

    @lru_cache(maxsize=1000)
    def summarize_text(self, text):
        summary = self.summarizer(text, max_length=150, min_length=50, do_sample=False)[0]['summary_text']
        return summary.strip()

    @lru_cache(maxsize=1000)
    def generate_text(self, prompt, max_length=200):
        inputs = self.tokenizer(prompt, return_tensors="pt", max_length=1024, truncation=True)
        summary_ids = self.model.generate(inputs.input_ids, num_beams=4, min_length=50, max_length=max_length, length_penalty=2.0, no_repeat_ngram_size=3)
        summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        return summary.strip()

    def compare_papers(self, papers):
        all_abstracts = " ".join([paper['abstract'] for paper in papers if paper['abstract'] != "N/A"])
        prompt = f"Compare and contrast the following research papers based on their abstracts:\n\n{all_abstracts}\n\nComparison:"
        return self.generate_text(prompt, max_length=300)

    def get_insights(self, papers):
        all_info = " ".join([f"{paper['title']} by {paper['author']} ({paper['year']}): {paper['abstract']}" for paper in papers if paper['abstract'] != "N/A"])
        prompt = f"Based on the following research papers, provide insights and potential areas for future research:\n\n{all_info}\n\nInsights:"
        return self.generate_text(prompt, max_length=300)

    @lru_cache(maxsize=100)
    def generate_report(self, query):
        papers = self.search_papers(query)
        
        report = {
            "topic": query,
            "relevant_papers": [],
            "comparison": None,
            "insights": None
        }
        
        for paper in papers:
            summary = self.summarize_text(paper['abstract'])
            report["relevant_papers"].append({
                "title": paper['title'],
                "author": paper['author'],
                "year": paper['year'],
                "summary": summary,
                "url": paper['url']
            })
        
        comparison = self.compare_papers(papers)
        report["comparison"] = comparison
        
        insights = self.get_insights(papers)
        report["insights"] = insights
        
        return report