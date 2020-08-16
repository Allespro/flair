# flair
*Half of an AirDrop substitute*

#### What:
Flair is written with one thing goal: make it easier to get files off an iPhone/iPad/etc.

Personally, I hate messing around with cloud file hosting or iTunes file sharing if I want a file from my phone on my computer. 
However, I don't own a Mac and can't just AirDrop myself files. This has always been an annoyance.

One day, I was looking through Workflow/Shortcuts on iOS and noticed there was a block that would send an HTTP request to a server of
the user's choosing. It turns out, it's possible to POST a homemade server any file you want from the share sheet with the right
Workflow/Shortcuts setup, which is very convenient indeed. 

This is the receiving server. It can create files. 

#### Use:

You can pack as many file operations as you'd like into a single request. 

Requests are formatted as JSON. The fields appear as follows:

	{
		"1": {						//must be a unique value for each action listed
			"TYPE": "FILEMOD",		//always FILEMOD
			"ACTION": "___",		//one of APPEND, CREATE, WRITE or REMOVE
			"TARGET": "___",		//filename
			"EXT": "___",			//[optional] file extension
			"BINARY": true/false,	//is data being sent base64 encoded binary?
			"DATA": "___",			//payload
			"BREAK": true/false		//[optional] for append operations, add newline after appending?
		}
	}
	
##### Notes:

* REMOVE action is not implemented and may be removed (yeah, yeah) in future - too much potential for destruction
* TARGET may include extension for simplicity - Workflow has trouble concatenating strings so EXT will be appended if present

## **Warning:**
This is intended for secured, local network use only. There is **no encryption or authentication**. Data is sent as plaintext (binaries are base64 encoded).

This is intentional, it keeps complexity down and limits processing required on the sending end.

**Do not use this over the Internet.**

**Do not use this on public or work networks.**

**Do not share your classified CIA documents with this.**

You have been warned, this is a **toy**. It will work locally and that's all it was designed to do.
