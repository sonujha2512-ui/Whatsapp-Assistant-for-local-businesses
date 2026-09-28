import json
import os

# path to the json file with all the FAQs
faq_file = os.path.join(os.path.dirname(__file__), 'faqs.json')

def load_faqs():
    f = open(faq_file, 'r', encoding='utf-8')
    data = json.load(f)
    f.close()
    return data


def find_answer(msg):
    faqs = load_faqs()
    msg = msg.lower()

    for topic in faqs:
        entry = faqs[topic]
        for kw in entry['keywords']:
            if kw.lower() in msg:
                return entry['answer']
    # nothing matched
    return None


def list_topics():
    faqs = load_faqs()
    topics = list(faqs.keys())
    return ', '.join(topics)