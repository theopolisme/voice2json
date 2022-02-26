voice2json
=============

*Export your Google Voice call & text history as JSON*

Google Takeout only offers HTML export of your Google Voice call and text message records. `voice2json` converts these HTML files into machine-readable JSON for easier analysis.

## Usage

*Note: Beautiful Soup 4 is a required dependency for HTML parsing. Install it using* `pip install beautifulsoup4`*.*

First, download your Google Voice call history as HTML from [Google Takeout](https://www.google.com/settings/takeout). Unzip the file and navigate to the `Voice/Calls` directory. Then run the `voice2json.py`, passing in the path to the calls directory, and you're all done:

```
$ python voice2json.py /path/to/Takeout/Voice/Calls /path/to/output.json
```

Slightly more detailed:

```
$ python voice2json.py -h
usage: voice2json.py [-h] source [output]

positional arguments:
  source      Source directory of call HTML files to convert
  output      File to write JSON output to (default: stdout)

optional arguments:
  -h, --help  show this help message and exit
```

## Output

`voice2json` produces a JSON file in the following format:

```js
{
	"records": [

		// Calls, voicemails, etc...
		{
			"date": "2013-01-27T04:21:24.000Z", // ISO-formatted date
			"duration": 56000.0, // If applicable, the duration of the call
			"tags": [ // Array of the tags(s) associated with the record (see below)
				"received",
				...
			],
			"contributors": [ // An array of participants in the call
				{
					"tel": "+01234567890", // Stringified telephone number containing country code
					"name": "John Doe" // Name (if known, otherwise an empty string)
				},
				...
			]
		},

		// Text messages
		{
			"date": "2014-05-07T19:26:51.780Z", // ISO-formatted start date of conversation
			"conversation": [ // A list of messages in the conversation
				{
					"date": "2014-05-07T19:26:51.780Z", // ISO-formatted date of message
					"message": "I'm right behind you.",
					"sender": {
						"tel": "+01234567890", // Stringified telephone number containing country code
						"name": "John Doe" // Name (if known, otherwise an empty string)
					}
				},
				...
			],
			"contributors": [
				{
					"tel": "+01234567890", // Stringified telephone number containing country code
					"name": "John Doe" // Name (if known, otherwise an empty string)
				},
				{
					"tel": "+01234567890", // Your phone number
					"name": "Me"
				}
			],
			"tags": [ // A list of tags for the conversation
				"inbox", 
				"sms"
			]
		}

		...
}
```

Possible tags include:

 - **received** &ndash; an incoming call, received and answered
 - **missed** &ndash; an incoming call that was not answered
 - **placed** &ndash; an outgoing call
 - **inbox** &ndash; an item in the Google Voice inbox (e.g., a voicemail)
 - **voicemail** &ndash; a voicemail message
 - **unread** &ndash; used in conjunction with a voicemail to indicate that it is unread
 - **sms** &ndash; a text message

Happy analyzing!
