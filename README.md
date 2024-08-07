# ChatGPT-cli
A simple python script for interfacing with ChatGPT in the command prompt.

## Usage
`chatgpt-cli.py --help`

    chatgpt-cli.py
    Usage:  chatgpt-cli.py --[option]
    Options:
            --help                          Display this help message.
            --key <keyfile>                 Specify an api key file. (Default behavior is to get this from $OPENAI_API_KEY.)
            --prompt "prompt"               Print reply from prompt and exit. (Default behavior is to run in interactive mode.)
            --max-history <number>          Set maximum chat memory for chatbot. (Doing this will decrease the size of api calls.)
            --log <logfile>                 Set a log file to save the chat history in.
            --model "model"                 Specify which model to use. (Defaults to gpt-4o-mini.)
            --system-message "message"      Provide the chatbot with some context or instructions about its behavior.


## Dependencies
The following are dependencies that you may need to install.
- requests
- prompt_toolkit

## Installation / Configuration
### Installation
1. Clone this git repository.

	`git clone https://github.com/joshuadeal/chatgpt-cli`

1. Change to repository directory.

	`cd ./chatgpt-cli/`

1. Install dependencies.

	`python -m pip install -r ./requires.txt`

### Configuration
1. You can create a json file with the value "apiKey" and pass it to the program each time you run it via the "--key" option, but this method is not recommended.

	Said json file should look something like this...
        
        {
                "apiKey": "Put your API key here."
        }
 
1. Your best bet is to set up the environmental variable "OPENAI_API_KEY"

   1. `echo "export OPENAI_API_KEY='put your api key here'" >> ~/.bashrc"`

   1. `source ~/.bashrc`

	To test if this has been done correctly run ```echo $OPENAI_API_KEY```. The output should be your API key.

Take care to keep API keys secure!
