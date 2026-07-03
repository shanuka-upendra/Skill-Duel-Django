import requests
import html


# OpenTDB category mapping
CATEGORY_MAP = {
    'coding': 18,   # Computer Science
    'math':   19,   # Mathematics
}


def fetch_questions_from_api(category, amount=5):
    """
    Fetch questions from Open Trivia Database API.
    Returns a list of question dicts or empty list if fails.
    """
    category_id = CATEGORY_MAP.get(category, 18)

    url = (
        f"https://opentdb.com/api.php"
        f"?amount={amount}"
        f"&category={category_id}"
        f"&difficulty=easy"
        f"&type=multiple"
    )

    try:
        response = requests.get(url, timeout=10)
        data     = response.json()

        if data['response_code'] != 0:
            return []

        questions = []
        for item in data['results']:
            # Decode HTML entities — API returns &amp; &quot; etc
            text     = html.unescape(item['question'])
            correct  = html.unescape(item['correct_answer'])
            wrongs   = [html.unescape(w) for w in item['incorrect_answers']]

            # Shuffle options so correct isn't always in same position
            import random
            all_options = [correct] + wrongs
            random.shuffle(all_options)

            # Map to a, b, c, d
            keys = ['a', 'b', 'c', 'd']
            correct_key = None
            options = {}

            for i, option in enumerate(all_options):
                options[keys[i]] = option
                if option == correct:
                    correct_key = keys[i]

            questions.append({
                'text':     text,
                'category': category,
                'option_a': options['a'],
                'option_b': options['b'],
                'option_c': options['c'],
                'option_d': options['d'],
                'correct':  correct_key,
            })

        return questions

    except Exception as e:
        print(f"OpenTDB API error: {e}")
        return []