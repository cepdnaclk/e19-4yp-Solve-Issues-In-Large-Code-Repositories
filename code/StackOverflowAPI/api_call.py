"""
ⓒ Debug.Ai 2025 Eshan Jayasundara

This file contains stackoverflow api calling functions.

DONE: add question answer matching mechanism like sorting them by question_id since both contain that we can use question_id to combine both as well
DONE: NOT_STARTED: check the repeated question_id s came with more than one requests
DONE: add advanced filtering method to filter old question answer pairs
DONE: update `qa_pairs = {"question_id":[],"creation_date":[],"link":[],"question":[],"accepted_answer":[],"question_vote":[],"answer_vote":[]}` accordingly and save a csv and upload to hugging face
NOT_POSSIBLE: Take 10 answers for each question if not add NULL but add a column to specify the vote count (answer columns should be in descending order based on votes from left to right)
DONE: print the remaining quota from the response -> response = requests.get(URL)
DONE: format the code following best code practices(optional)


Example question:

{'tags': ['python',
          'encryption',
          'whatsapp',
          'whatsapp-cloud-api',
          'whatsapp-flows'],
 'owner': {'account_id': 39041909,
           'reputation': 11,
           'user_id': 29077067,
           'user_type': 'registered',
           'profile_image': 'https://www.gravatar.com/avatar/cba5484c9eafee415b547b83bd871ea0?s=256&d=identicon&r=PG&f=y&so-version=2',
           'display_name': 'S&#233;amus CAREY',
           'link': 'https://stackoverflow.com/users/29077067/s%c3%a9amus-carey'},
 'is_answered': False,
 'view_count': 115,
 'answer_count': 1,
 'score': 1,
 'last_activity_date': 1737562929,
 'creation_date': 1736251700,
 'last_edit_date': 1736253147,
 'question_id': 79335941,
 'content_license': 'CC BY-SA 4.0',
 'link': 'https://stackoverflow.com/questions/79335941/cannot-decrypt-rsa-key-and-complete-whatsapp-flows-healthcheck',
 'title': 'Cannot decrypt RSA key and complete WhatsApp flows healthcheck',
 'body': <question_text>}


Example answer:

{'owner': {'account_id': 473095,
           'reputation': 87959,
           'user_id': 882003,
           'user_type': 'registered',
           'accept_rate': 78,
           'profile_image': 'https://www.gravatar.com/avatar/de71acd9a8eab73186dea35aea7a68f2?s=256&d=identicon&r=PG',
           'display_name': 'john',
           'link': 'https://stackoverflow.com/users/882003/john'},
 'is_accepted': True,
 'score': 3,
 'last_activity_date': 1735712245,
 'creation_date': 1735712245,
 'answer_id': 79321227,
 'question_id': 79321224,
 'content_license': 'CC BY-SA 4.0',
 'body': <answer_text>}
"""


import httpx
import asyncio
from typing import List, Dict, Any, Annotated
from utils import *

async def fetch(client, url):
    response = await client.get(url)
    return response.json()

async def extract_questions(
    domain: str, 
    subdomain: str, 
    api_version: str, 
    order: str, 
    sort_by: str, 
    min: int, 
    from_date: Annotated[str, "Format: YYYY-MM-DD"], 
    to_date: Annotated[str, "Format: YYYY-MM-DD"], 
    tags: List, 
    site: str, 
    pagesize: int, 
    page: int
    ) -> List[Dict[str, Any]]:
    """
    Fetch questions from the Stack Exchange API given the date range
    """
    tag_string = ""
    for tag in tags:
        tag_string = tag_string + f'{tag};'
    tag_string = tag_string[:-1]

    URL = f"https://{subdomain}.{domain}/{api_version}/questions?order={order}&sort={sort_by}&min={min}&fromdate={str_to__midnight_utc(str_date=from_date)}&todate={str_to__midnight_utc(str_date=to_date)}&site={site}&tagged={tag_string}&page={page}&pagesize={pagesize}&filter=withbody"
    async with httpx.AsyncClient() as client:
        data = await fetch(client, URL)
    print(f"""
    +-----------+
    | Attention |
    +-----------+
    quota_max:{data['quota_max']}, quota_remaining:{data['quota_remaining']}\n""")
    return data.get("items", [])

async def extract_answers_by_question_id(
    ids: List, 
    domain: str, 
    subdomain: str, 
    api_version: str, 
    order: str, 
    sort_by: str,  
    pagesize: int
    ) -> List[Dict[str, Any]]:
    """
    Fetch answers from the Stack Exchange API given the question ids
    """
    ids_string = ""
    for id in ids:
        ids_string = ids_string + f'{id};'
    ids_string = ids_string[:-1]
    URL = f"https://{subdomain}.{domain}/{api_version}/questions/{ids_string}/answers?order={order}&pagesize={pagesize}&sort={sort_by}&site=stackoverflow&filter=withbody"
    async with httpx.AsyncClient() as client:
        data = await fetch(client, URL)

    print(f"""
    +-----------+
    | Attention |
    +-----------+
    quota_max:{data['quota_max']}, quota_remaining:{data['quota_remaining']}\n""")
    return data.get("items", [])

async def extract_answers_by_answer_id(
    ids:List, 
    domain: str, 
    subdomain: str, 
    api_version: str, 
    order: str, 
    sort_by: str,  
    pagesize: int
    ) -> List[Dict[str, Any]]:
    """
    Fetch answers from the Stack Exchange API given the answer ids
    """
    ids_string = ""
    for id in ids:
        ids_string = ids_string + f'{id};'
    ids_string = ids_string[:-1]
    URL = f"https://{subdomain}.{domain}/{api_version}/answers/{ids_string}?order={order}&sort={sort_by}&pagesize={pagesize}&site=stackoverflow&filter=withbody"
    async with httpx.AsyncClient() as client:
        data = await fetch(client, URL)

    print(f"""
    +-----------+
    | Attention |
    +-----------+
    quota_max:{data['quota_max']}, quota_remaining:{data['quota_remaining']}\n""")
    return data.get("items", [])

def get_question_answer_pairs(from_date, to_date, tags):
    """
    Fetch question answer pairs from the Stack Exchange API using the above `extract_questions` `extract_answers_by_answer_id` functions
    """
    qa_pairs = {
        "question_id":[],
        "creation_date":[],
        "link":[],
        "question":[],
        "accepted_answer":[],
        "question_vote":[],
        "answer_vote":[]
        }
    
    questions = asyncio.run(
        extract_questions(
            domain="com", 
            subdomain="api.stackexchange", 
            api_version="2.3", order="desc", 
            sort_by="votes", min=1, 
            from_date=from_date, 
            to_date=to_date, 
            tags=tags, 
            site="stackoverflow", 
            pagesize=100, 
            page=1
            )
        )
    
    qa_dict = {}
    """
    `qa_dict` storage format(helpful to map question answer pairs without sorting):
    {
        <question_id1>:{
            "question":<question_text>, 
            "link":<link>,
            "question_vote":<score>
        },
        <question_id2>:{
            "question":<question_text>, 
            "link":<link>, 
            "question_vote":<score>
        },
        ...
    }
    """

    ansids = []
    for i, question in enumerate(questions):
        if not question["is_answered"]:
            continue

        if not 'accepted_answer_id' in list(question.keys()):
            continue
        
        ansids.append(question["accepted_answer_id"])

        qa_dict.setdefault(question["question_id"], {})["question"] = clean_text(question["body"])
        qa_dict.setdefault(question["question_id"], {})["link"] = question["link"]
        qa_dict.setdefault(question["question_id"], {})["question_vote"] = question["score"]
        qa_dict.setdefault(question["question_id"], {})["creation_date"] = question["creation_date"]
        
    qids = list(qa_dict.keys())

    answers = asyncio.run(
        extract_answers_by_answer_id(
            ids=ansids, 
            domain="com", 
            subdomain="api.stackexchange", 
            order="desc", 
            sort_by="activity", 
            api_version="2.3", 
            pagesize=len(ansids)
            )
        )

    accepted_answers_count = 0
    answer_to_question_map_count = 0

    for answer in answers:
        if not answer["is_accepted"]:
            continue

        accepted_answers_count += 1

        if not answer["question_id"] in qids:
            continue

        answer_to_question_map_count += 1

        qa_pairs["question_id"].append(answer["question_id"])
        qa_pairs["link"].append(qa_dict[answer["question_id"]]["link"])
        qa_pairs["question"].append(qa_dict[answer["question_id"]]["question"])
        qa_pairs["accepted_answer"].append(clean_text(answer["body"]))
        qa_pairs["question_vote"].append(qa_dict[answer["question_id"]]["question_vote"])
        qa_pairs["creation_date"].append(midnight_utc_to_str(qa_dict[answer["question_id"]]["creation_date"]))
        qa_pairs["answer_vote"].append(answer["score"])

    print(f"Followings should be equal,")
    print(f"Number of questions extracted: {len(qids)}")
    print(f"Number of answers expected: {len(ansids)}")
    print(f"Number of answers received: {len(ansids)}")
    print(f"    |- Number of answers each having a mapping to extracted questions: {answer_to_question_map_count}")
    print(f"    '-Number of accepted answers: {accepted_answers_count}\n")

    return qa_pairs