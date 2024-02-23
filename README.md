# ChatGPT-cli
A simple python script for interfacing with ChatGPT in the command prompt.

## Usage
```chatgpt-cli.py --help```
```
chatgpt-cli.py
Usage:  ./chatgpt-cli.py --[option]
Options:
        --help                  Display this help message.
        --key <keyfile>         Specify an api key file.(Default behavior is to get this from $OPENAI_API_KEY)
        --prompt "prompt"       Print reply from prompt and exit. (Default behavior is to run in interactive mode.)
```

## Dependencies
The following are dependencies that you may need to install.
- requests
- prompt_toolkit
