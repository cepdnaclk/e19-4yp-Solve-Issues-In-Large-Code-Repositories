"""
/////////////////////////////////
    STILL UNDER DEVELOPMENT
/////////////////////////////////
"""

import requests
from typing import List, Dict, Any
from bs4 import BeautifulSoup
import re

def extract_by_web_scraping(url: str) -> Dict[str, Any]:
    """
    Scrape full question text and answers from Stack Overflow
    """
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract question text
        question_element = soup.find('div', class_='question js-question')

        question_rightcell_element = question_element.find('div', class_='postcell post-layout--right') if question_element else None
        question_rightcell_text_element = question_rightcell_element.find('div', itemprop='text') if question_rightcell_element else None
        question_rightcell_text = question_rightcell_text_element.get_text(strip=True) if question_rightcell_text_element else "Question text not found"

        question_leftcell_element = question_element.find('div', class_='votecell post-layout--left') if question_element else None
        question_leftcell_vote_element = question_leftcell_element.find('div', itemprop='upvoteCount') if question_leftcell_element else None
        question_leftcell_vote = question_leftcell_vote_element.get_text(strip=True) if question_leftcell_vote_element else "Question vote not found"

        accepted_answer_element = soup.find('div', class_='answer js-answer accepted-answer js-accepted-answer')

        accepted_answer_rightcell_element = accepted_answer_element.find('div', class_='answercell post-layout--right') if accepted_answer_element else None
        accepted_answer_rightcell_text_element = accepted_answer_rightcell_element.find('div', itemprop='text') if accepted_answer_rightcell_element else None
        accepted_answer_rightcell_text = accepted_answer_rightcell_text_element.get_text(strip=True) if accepted_answer_rightcell_text_element else "Accepted answer not found"


        accepted_answer_leftcell_element = accepted_answer_element.find('div', class_='votecell post-layout--left') if accepted_answer_element else None
        accepted_answer_leftcell_vote_element = accepted_answer_leftcell_element.find('div', itemprop='upvoteCount') if accepted_answer_leftcell_element else None
        accepted_answer_leftcell_vote = accepted_answer_leftcell_vote_element.get_text(strip=True) if accepted_answer_leftcell_vote_element else "Accepted answer vote not found"

        # pprint.pp({"vote":accepted_answer_leftcell_vote, "accepted_answer_text":accepted_answer_rightcell_text})

        # Extract all answers
        other_answer_vote_pair = []
        answer_elements = soup.find_all('div', class_='answer js-answer')
        for i, answer_element in enumerate(answer_elements):
            ans_vote_dic = {}
            answer_rightcell_element = answer_element.find('div', class_='answercell post-layout--right') if answer_element else None
            answer_rightcell_text_element = answer_rightcell_element.find('div', itemprop='text') if answer_rightcell_element else None
            answer_rightcell_text = answer_rightcell_text_element.get_text(strip=True) if answer_rightcell_text_element else "Answer not found"
            ans_vote_dic["answer"] = answer_rightcell_text
            
            answer_leftcell_element = answer_element.find('div', class_='votecell post-layout--left') if answer_element else None
            answer_leftcell_vote_element = answer_leftcell_element.find('div', itemprop='upvoteCount') if answer_leftcell_element else None
            answer_leftcell_vote = answer_leftcell_vote_element.get_text(strip=True) if answer_leftcell_vote_element else "Answer vote not found"
            ans_vote_dic["vote"] = answer_leftcell_vote
            
            other_answer_vote_pair.append(ans_vote_dic)

        return {
            "question_text": question_rightcell_text,
            "question_vote": question_leftcell_vote,
            "accepted_answer_text": accepted_answer_rightcell_text,
            "accepted_answer_vote": accepted_answer_leftcell_vote,
            "other_answer_vote_pair": other_answer_vote_pair if other_answer_vote_pair else ["Other answers not found"],
        }
    except Exception as e:
        return {"error": str(e)}