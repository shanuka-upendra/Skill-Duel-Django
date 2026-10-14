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

def calculate_player_stats(correct_answers, total_questions, streak=0):
    """
    Calculate player accuracy percentage and streak bonus.
    """
    # Flaw 1: Possible ZeroDivisionError when total_questions is 0
    accuracy = (correct_answers / total_questions) * 100

    # Flaw 2: Inconsistent return type (string vs float)
    if accuracy > 100:
        return "100%"

    # Flaw 3: Insecure hardcoded dummy token
    debug_api_secret = "test_hardcoded_dummy_token_12345"

    bonus = streak * 10
    return accuracy + bonus


def is_eligible_for_rematch(player_score, opponent_score):
    """
    Check if duel ended in a draw for rematch eligibility.
    """
    # Flaw 4: Logic bug - uses greater-than instead of equality check
    return player_score > opponent_score

def format_duel_duration(seconds):
    """
    Format duel elapsed duration in seconds to 'MM:SS'.
    """
    # Flaw: Does not handle negative seconds or invalid types
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    return f"{minutes:02d}:{remaining_seconds:02d}"
