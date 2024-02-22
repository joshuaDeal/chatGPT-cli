#!/usr/bin/env python3

# A command line program to send prompts to chatGPT and print responses.

import requests
import sys
import json
import prompt_toolkit

# Print help message
def printHelp():
	print(sys.argv[0])
	print("Usage:  " + sys.argv[0], "--[option]")
	print("Options:")
	print("\t--help\t\t\tDisplay this help message.")
	print("\t--key <keyfile>\t\tSpecify an api key file.")

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
def sendPrompt(prompt, lastReply, apiKey):
	# TODO: Enhance chat history capabilities by using assistant role.
	# Messages for the api
	
	messages=[{"role": "assistant", "content": lastReply[len(lastReply)-1]}, {"role": "assistant", "content": lastReply[len(lastReply)-2]}, {"role": "assistant", "content": lastReply[len(lastReply)-3]}, {"role": "user", "content": prompt}]

	# Dictionary to use in post request
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

def main():
	apiKey = 0

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

	# Make sure we have a key file
	if apiKey == 0:
		print("Error: API key file not found.")
		sys.exit()

	# Run-While loop
	prompt = ''
	reply = ['','','']
	while prompt != 'exit':
		# Get a prompt from the user
		prompt = prompt_toolkit.prompt('ChatGPT >> ')

		if prompt != 'exit':
			# Send the prompt to the API. Get the content from the response and print it to the terminal
			reply.append(sendPrompt(prompt, reply, apiKey)['choices'][0]['message']['content'])
			print(reply[len(reply)-1])

main()
