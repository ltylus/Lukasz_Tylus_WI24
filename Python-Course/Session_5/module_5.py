from collections import Counter
import os
from pathlib import Path
# from random import choice
from random import seed
from typing import List, Union
import re
import requests
from requests.exceptions import RequestException
from requests.exceptions import ConnectionError
from gensim.utils import simple_preprocess


S5_PATH = Path(os.path.realpath(__file__)).parent

PATH_TO_NAMES = S5_PATH / "names.txt"
PATH_TO_SURNAMES = S5_PATH / "last_names.txt"
PATH_TO_OUTPUT = S5_PATH / "sorted_names_and_surnames.txt"
PATH_TO_TEXT = S5_PATH / "random_text.txt"
PATH_TO_STOP_WORDS = S5_PATH / "stop_words.txt"

import random

def task_1():
    random.seed(1)
    
    try:
        with open(PATH_TO_NAMES, 'r') as names_file, open(PATH_TO_SURNAMES, 'r') as surnames_file:
            names = sorted(name.strip().lower() for name in names_file)
            surnames = [surname.strip().lower() for surname in surnames_file]
        
        with open(PATH_TO_OUTPUT, 'w') as output_file:
            for name in names:
                surname = random.choice(surnames)
                output_file.write(f"{name} {surname}\n")
    except FileNotFoundError as e:
        print(f"File not found: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


def task_2(top_k: int):
    try:
        with open('random_text.txt', 'r') as text_file, open('stop_words.txt', 'r') as stop_words_file:
            text = text_file.read().lower()
            stop_words = set(word.strip() for word in stop_words_file)
        
        words = [word for word in re.findall(r'\b[a-z]+\b', text) if word not in stop_words]
        word_counts = Counter(words)
        
        return word_counts.most_common(top_k)
    except FileNotFoundError as e:
        print(f"File not found: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


def task_3(url: str):
   try:
        response = requests.get(url)
        response.raise_for_status()
        return response
    except RequestException as e:
        raise e


def task_4(data: List[Union[int, str, float]]):
    total = 0
    for item in data:
        try:
            total += float(item)
        except ValueError:
            raise TypeError(f"Cannot convert {item} to float")
    return total


def task_5():
    try:
        num1, num2 = input("Enter two numbers separated by space: ").split()
        result = float(num1) / float(num2)
        print(result)
    except ZeroDivisionError:
        print("Can't divide by zero")
    except ValueError:
        print("Entered value is wrong")
