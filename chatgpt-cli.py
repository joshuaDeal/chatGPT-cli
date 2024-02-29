#!/usr/bin/env python3

# A command line program to send prompts to chatGPT and print responses.

import requests
import sys
import os
import json
import prompt_toolkit

# Print help message
def printHelp():
	print(sys.argv[0])
	print("Usage:  " + sys.argv[0], "--[option]")
	print("Options:")
	print("\t--help\t\t\tDisplay this help message.")
	print("\t--key <keyfile>\t\tSpecify an api key file. (Default behavior is to get this from $OPENAI_API_KEY.)")
	print("\t--prompt \"prompt\"\tPrint reply from prompt and exit. (Default behavior is to run in interactive mode.)")
	print("\t--max-history <number>\tSet maximum chat memory for chatbot. (Doing this will decrease the size of api calls.)")
	print("\t--log <logfile>\t\tSet a log file to save the chat history in.")

# TODO: Make api key handling more secure
# Get an api key from a json file
def getApiKey(keyFile):
	try:
		with open(keyFile, 'r') as file:
			data = json.load(file)
			apiKey = data.get('apiKey')
		return apiKey
	except FileNotFoundError:
		return 0

# Send a http POST request to the API along with the API key and user's prompt. Will return response from API.
def sendPrompt(prompt, history, apiKey):
	# Give the chatbot a chat history for context.
	messages=[]
	for i in range(len(history)):
		messages.append({"role": "assistant", "content": history[i]})

	# Also give the chatbot the user's current prompt.
	messages.append({"role": "user", "content": prompt})

	# Other useful data for the chatbot.
	data = {"model": "gpt-3.5-turbo", "messages": messages}

	# Headers for the post request
	headers = {"Content-Type": "application/json", "Authorization": f"Bearer {apiKey}", "OpenAI-Beta": "assistants=v1"}

	# Send the post request
	response = requests.post('https://api.openai.com/v1/chat/completions', json=data, headers=headers)

	# Check if we got a successful response
	if response.status_code == 200:
		return response.json()
	else:
		print("Error:", response.status_code)
		return response.status_code()

def updateLog(content, logFile):
	with open(logFile, 'a') as file:
		file.writelines(content)
		file.write('\n')

def main():
	apiKey = 0
	prompt = ''
	history = []
	maxHist = 0
	runOnce = False
	logMode = False

	# Check if $OPENAI_API_KEY exists. use it if it dose
	if os.getenv('OPENAI_API_KEY') != '':
		apiKey = os.getenv('OPENAI_API_KEY')

	# Evaluate options
	# TODO: Implement error handling for when incorrect arguments are provided.
	for i in range(len(sys.argv)):
		# Print help message and exit
		if sys.argv[i] == "--help" or sys.argv[i] == "-h":
			printHelp()
			sys.exit()
		# Let user pick a key file
		elif sys.argv[i] == "--key" or sys.argv[i] == "-k":
			apiKey = getApiKey(sys.argv[i+1])
		# Allow the user to send a single prompt and quit
		elif sys.argv[i] == "--prompt" or sys.argv[i] == "-p":
			runOnce = True
			prompt = sys.argv[i+1]
		# Allow user to set a maximum history value
		elif sys.argv[i] == "--max-history" or sys.argv[i] == "-m":
			maxHist = int(sys.argv[i+1])
		# Allow user to enable log mode.
		elif sys.argv[i] == "--log" or sys.argv[i] == "-l":
			logMode = True
			logFile = sys.argv[i+1]

	# Make sure we have a key file
	if apiKey == 0:
		print("Error: API key file not found.")
		sys.exit()

	# In case we are in run once mode	
	if runOnce:
		#Send prompt to api
		reply = sendPrompt(prompt, history, apiKey)['choices'][0]['message']['content']
		print(reply)
		sys.exit()

	# Run-While loop
	while prompt != 'exit':
		# Get a prompt from the user
		prompt = prompt_toolkit.prompt('ChatGPT >> ')

		if prompt != 'exit':
			# Send the prompt to the API. Get the content from the response and save it as reply.
			reply = sendPrompt(prompt, history, apiKey)['choices'][0]['message']['content']

			# Remove first item from history if maxHistory is set
			if maxHist > 0:
				if len(history) > maxHist:
					history.pop(0)

			# Update history.
			history.append(f"User: {prompt}\nChatbot: {reply}")

			# Print the reply
			print("\n" + reply + "\n")

			if logMode:
				updateLog(history[-1], logFile)

main()
