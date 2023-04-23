# opeani-fomatting

## Initial project description

I want you to create a complex script that will do the following:

1. Downloads or updates the git@github.com:openai/evals.git repository to the openai-evals directory
2. use the previously created script to output prompt from the openai-evals/evals directory to the input.txt file. I want to make two modification to the script:
   1. I want not to collect empty prompts
   2. I want to remove any duplicate prompts
3. Nex,I want to call the proper Openai endpoint to loop over the input.txt file to answer the "Can you distinguish between the task and the output formatting instructions? if so, please output the instruction with an explanation" question. I want to save the result to the promts.jsonl file with "prompt" and "description" fields. See the beginning of chat for examples of the output.
4.  After that, I want to loop over the promts.jsonl file call the a proper Openai endpoint ti=o determine any prompts, that result the same formatting. iwant you to remove any duplicates, leave the best input only. I want to save the result to the result.jsonl file with prompt and description fields.

Use the `OPENAI_API_KEY` environment variables to connect the openai rest endpoint
