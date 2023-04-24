import os
import tiktoken

def count_tokens_in_file(file_path, encoder):
    token_count = 0

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            tokens = encoder.encode(line)
            token_count += len(tokens)

    return token_count

def main():
    # Get the encoding for the "cl100k_base" model
    encoder = tiktoken.get_encoding("cl100k_base")

    input_file_path = os.path.join('data', 'inputs.txt')
    token_count = count_tokens_in_file(input_file_path, encoder)

    formatted_token_count = f"{token_count:,}"
    print(f"Token count for the file '{input_file_path}': {formatted_token_count}")

if __name__ == "__main__":
    main()
