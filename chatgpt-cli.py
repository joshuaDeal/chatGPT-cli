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
	print("\t--help\t\t\t\tDisplay this help message.")
	print("\t--key <keyfile>\t\t\tSpecify an api key file. (Default behavior is to get this from $OPENAI_API_KEY.)")
	print("\t--prompt \"prompt\"\t\tPrint reply from prompt and exit. (Default behavior is to run in interactive mode.)")
	print("\t--max-history <number>\t\tSet maximum chat memory for chatbot. (Doing this will decrease the size of api calls.)")
	print("\t--log <logfile>\t\t\tSet a log file to save the chat history in.")
	print("\t--model \"model\"\t\t\tSpecify which model to use. (Defaults to gpt-4o-mini.)")
	print("\t--system-message \"message\"\tProvide the chatbot with some context or instructions about its behavior.")

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
def sendPrompt(prompt, systemMessage, history, apiKey, model):
	messages=[]

	# Give the chatbot the system message
	if systemMessage != '':
		messages.append({"role": "system", "content": systemMessage})

	# Give the chatbot a chat history for context.
	if "exchanges" in history:
		messages.extend(history["exchanges"])

	# Also give the chatbot the user's current prompt.
	messages.append({"role": "user", "content": prompt})

	# Other useful data for the chatbot.
	data = {"model": model, "messages": messages}

	# Headers for the post request
	headers = {"Content-Type": "application/json", "Authorization": f"Bearer {apiKey}", "OpenAI-Beta": "assistants=v1"}

	try:
		# Send the post request
		response = requests.post('https://api.openai.com/v1/chat/completions', json=data, headers=headers)

		# Raise HTTPError for bad responses
		response.raise_for_status()

		return response.json()
	except requests.exceptions.HTTPError as httpError:
		print(f"HTTP error occured: {httpError}")
		return {"error": f"HTTP error: {response.status_code} - {response.text}"}
	except requests.exceptions.ConnectionError:
		print(f"Connection error: Failed to reach API")
		return {"error": "Connection error: Unable to reach API."}
	except requests.exceptions.Timeout:
		print("Timeout error: API response took too long.")
		return {"error": "Timeout error: The API took too long to respond."}
	except requests.exceptions.RequestException as req_err:
		print(f"Request error occurred: {req_err}")
		return {"error": f"Request error: {req_err}"}

def updateLog(history, logFile):
	try:
		with open(logFile, 'w') as file:
			json.dump(history, file, indent=4)
	except Exception as e:
		print(f"Failed to write to log file: {e}")

# Evaluate options
def evalArguments():
	# TODO: Implement error handling for when incorrect arguments are provided.

	# Default values
	output = {'apiKey': 0,'prompt': '','systemMessage': '','model': 'gpt-4o-mini','maxHist': 0,'runOnce': False, 'logMode': False}

	for i in range(len(sys.argv)):
		# Print help message and exit
		if sys.argv[i] == "--help" or sys.argv[i] == "-h":
			printHelp()
			sys.exit()
		# Let user pick a key file
		elif sys.argv[i] == "--key" or sys.argv[i] == "-k":
			output['apiKey'] = getApiKey(sys.argv[i+1])
		# Allow the user to send a single prompt and quit
		elif sys.argv[i] == "--prompt" or sys.argv[i] == "-p":
			output['runOnce'] = True
			output['prompt'] = sys.argv[i+1]
		# Allow user to set a maximum history value
		elif sys.argv[i] == "--max-history" or sys.argv[i] == "-m":
			output['maxHist'] = int(sys.argv[i+1])
		# Allow user to enable log mode.
		elif sys.argv[i] == "--log" or sys.argv[i] == "-l":
			output['logMode'] = True
			output['logFile'] = sys.argv[i+1]
		elif sys.argv[i] == "--model" or sys.argv[i] == "-M":
			output['model'] = sys.argv[i+1]
		# Allow user to set a system message
		elif sys.argv[i] == "--system-message" or sys.argv[i] == "-s":
			output['systemMessage'] = sys.argv[i+1]

	return output

def main():
	history = {"exchanges": []}

	# Evaluate options
	arguments = evalArguments()

	# Check if $OPENAI_API_KEY exists. use it if it dose
	if os.getenv('OPENAI_API_KEY') != '':
		arguments['apiKey'] = os.getenv('OPENAI_API_KEY')

	# Make sure we have a key file
	if arguments['apiKey'] == 0:
		print("Error: API key file not found.")
		sys.exit()

	# In case we are in run once mode	
	if arguments['runOnce']:
		# Send the prompt to the API.
		replyData = sendPrompt(arguments['prompt'],arguments['systemMessage'], history, arguments['apiKey'], arguments['model'])

		# Check API response for errors.
		if "error" in replyData:
			print(f"API Error: {replyData['error']}")
			sys.exit(1)
		elif "choices" in replyData and len(replyData["choices"]) > 0:
			reply = replyData["choices"][0]["message"]["content"]
			print(reply)
			sys.exit(1)
		else:
			print("Error: Unexpected API response format.")
			sys.exit(1)

	# Run-While loop
	while arguments['prompt'] != 'exit':
		# Get a prompt from the user
		arguments['prompt'] = prompt_toolkit.prompt('ChatGPT >> ')

		if arguments['prompt'] != 'exit':
			# Send the prompt to the API.
			replyData = sendPrompt(arguments['prompt'],arguments['systemMessage'], history, arguments['apiKey'], arguments['model'])

			# Check API response for errors.
			if "error" in replyData:
				print(f"API Error: {replyData['error']}")
				sys.exit(1)
			elif "choices" in replyData and len(replyData["choices"]) > 0:
				reply = replyData["choices"][0]["message"]["content"]
			else:
				print("Error: Unexpected API response format.")

			# Remove first item from history if maxHistory is set
			if arguments['maxHist'] > 0:
				excess = len(history["exchanges"]) - 2 * arguments['maxHist']
				if excess >= 2:
					history["exchanges"] = history["exchanges"][excess:]

			# Update history.
			history["exchanges"].append({"role": "user", "content": arguments["prompt"]})
			history["exchanges"].append({"role": "assistant", "content": reply})

			# Print the reply
			print("\n" + reply + "\n")

			if arguments['logMode']:
				updateLog(history, arguments['logFile'])

if __name__ == "__main__":
	main()
