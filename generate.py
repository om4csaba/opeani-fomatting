from collections import OrderedDict
from langdetect import detect
import argparse
import backoff
import git
import json
import openai
import os
import re

def update_repo(repo_url, local_dir):
    if os.path.exists(local_dir):
        repo = git.Repo(local_dir)
        origin = repo.remotes.origin
        origin.pull()
    else:
        repo = git.Repo.clone_from(repo_url, local_dir)
    return repo

def extract_prompts(folder_path):
    prompts = set()
    content_pattern = re.compile(r'content\s*:\s*([^,}]+)')

    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".jsonl"):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        data = json.loads(line)
                        input_data = data.get('input', [])
                        for item in input_data:
                            if isinstance(item, str):
                                match = content_pattern.search(item)
                                if match:
                                    content = match.group(1).strip()
                                    if content:
                                        prompts.add(content)
                            elif isinstance(item, dict):
                                content = item.get('content')
                                if content:
                                    prompts.add(content)
    return prompts

def is_english(text):
    try:
        lang = detect(text)
        return lang == 'en'
    except:
        return False

def save_prompts(prompts, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        for prompt in prompts:
            prompt = prompt.replace('\n', ' ')  # Replace newlines with spaces
            prompt = re.sub(r'\s+', ' ', prompt)  # Collapse multiple spaces into a single space
            prompt = prompt.strip()  # Remove leading and trailing spaces
            if prompt and is_english(prompt):
                f.write(prompt + '\n')

@backoff.on_exception(backoff.expo, openai.error.RateLimitError, max_tries=10)
def call_openai_api_with_backoff(prompt):
    openai.api_key = os.environ["OPENAI_API_KEY"]

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=150,
        n=1,
        temperature=0.5,
    )
    message = response['choices'][0]['message']['content'].strip()
    return message

def main():
    parser = argparse.ArgumentParser(description='Process prompts and interact with OpenAI API.')
    parser.add_argument('--update_evals', action='store_true', help='Download or update the git repository')
    parser.add_argument('--extract_prompts', action='store_true', help='Extract and save prompts to inputs.txt')
    parser.add_argument('--extract_formats', action='store_true', help='Call OpenAI API for each prompt and save the results to prompts.jsonl')

    args = parser.parse_args()

    local_dir = 'openai-evals'
    prompts = set()

    if args.update_evals:
        # Step 1: Download or update the repository
        repo_url = 'git@github.com:openai/evals.git'
        update_repo(repo_url, local_dir)

    if args.extract_prompts:
        # Step 2: Extract and save prompts to inputs.txt
        folder_path = os.path.join(local_dir, 'evals')
        output_file = 'data/inputs.txt'
        prompts = extract_prompts(folder_path)
        save_prompts(prompts, output_file)
    elif args.extract_formats:
        # Load prompts from inputs.txt if extract_prompts is not run
        with open('data/inputs.txt', 'r', encoding='utf-8') as f:
            prompts = set(line.strip() for line in f)

    if args.extract_formats:
        # Step 3: Call OpenAI API for each prompt and save the results to prompts.jsonl
        with open('data/prompts.jsonl', 'w', encoding='utf-8') as f:
            for prompt in prompts:
                question = f"Can you distinguish between the task and the output formatting instructions? if so, please output the instruction with an explanation. Here is the prompt: {prompt}"
                response = call_openai_api_with_backoff(question)
                result = {"prompt": prompt, "description": response}
                f.write(json.dumps(result) + '\n')

        # Loop over prompts.jsonl, remove duplicates and save results to result.jsonl
        descriptions = OrderedDict()
        with open('data/prompts.jsonl', 'r', encoding='utf-8') as f:
            for line in f:
                data = json.loads(line)
                prompt = data['prompt']
                description = data['description']
                if description not in descriptions:
                    descriptions[description] = prompt

        with open('data/result.jsonl', 'w', encoding='utf-8') as f:
            for description, prompt in descriptions.items():
                result = {"prompt": prompt, "description": description}
                f.write(json.dumps(result) + '\n')

if __name__ == "__main__":
    main()
