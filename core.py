from http import server
from http import HTTPStatus as status

import json
import base64
import socket

from os import path

def main():

	ip = ('192.168.2.144', 80); # change this to local ip

	httpserver = server.HTTPServer(ip, requestHandler);

	try:
		httpserver.serve_forever()
	except KeyboardInterrupt:
		print("Goodbye.")
		return

class requestHandler(server.BaseHTTPRequestHandler):
	hostnames = {}

	# for head and get requests, reply that nothing is available
	# there are no pages being served, so this is an easy solution
	def do_HEAD(s):
		s.send_error(status.NO_CONTENT, 'Ryanair in San Diego?')
		s.end_headers()

	def do_GET(s):
		s.send_error(status.NO_CONTENT, 'Stay on the line, we\'re tracing your call.')
		s.end_headers()

	# for put, just run post routine
	def do_PUT(s):
		s.do_POST()

	def do_POST(s):
		# ensure there's a length field provided
		try:
			content_length = int(s.headers['Content-Length'])
		except Exception as e:
			s.send_response(status.LENGTH_REQUIRED)
			s.end_headers()
			return

		sender = s.client_address[0]

		if sender not in s.hostnames:
			print("Unknown sender [" + sender + "], resolving hostname. Please wait...")
			try:
				s.hostnames[sender] = str(socket.gethostbyaddr(sender)[0])
				print("Identified [" + sender + "] as \"" + s.hostnames[sender] + "\"")
			except Exception as e: # something went wrong, probably a timeout
				print("Error resolving hostname!")
				s.hostnames[sender] = "Unknown"

		sender_hostname = s.hostnames[sender]

		post_data = s.rfile.read(content_length)

		try:
			ua = s.headers["User-Agent"]
		except Exception:
			print("ERROR: NO USER AGENT")
			s.send_response(status.BAD_REQUEST)
			s.end_headers()
			return

		# print(ua)

		if 'Workflow' in ua:
			src_type = 'WF'
		elif 'Shortcuts' in ua:
			src_type = 'SC'
		else:
			src_type = 'O'

		try:
			json_data = json.loads(post_data)

			# not all parameters will be used for all requests - unused data is ignored and may be omitted
			#
			# activity:		the dictionary defining the parameters of the action
			# -> type: 		the category of action being requested
			# -> action:	the specific action requested
			# -> target:	the action's target
			# -> ext:		[optional] target file extension - Workflow has trouble combining filename and extension
			# 				if this is present, it will be appended to the end of the filename, otherwise, only filename is used
			# -> binary:	boolean file type flag
			# -> overwrite: overwrite or rename existing files?
			# -> data:		data to apply to action
			# -> break:		newline on appending?

			for aindex, activity in json_data.items():
				
				if (activity['TYPE'] == 'FILEMOD'): # file modification

					action = activity['ACTION']

					# filename field
					ftarget = ''
					# extension field
					fext = ''

					# try separate name and extensions
					try:
						ftarget = activity['TARGET']
						fext = '.' + activity['EXT']

					# then try splitting the full filename into name and extension
					except Exception:
						try:
							fxi = activity['TARGET'].rfind('.')
							ftarget = activity['TARGET'][:fxi]
							fext = activity['TARGET'][fxi:]
						
						# neither worked, so just place as filename
						except Exception:
							ftarget = activity['TARGET']
							fext = ''


					target = 'files/' + ftarget + fext

					if (action == 'CREATE'):
						open(target, 'w').close()

					elif (action == 'WRITE'):
						data = activity['DATA']
						binary =  activity['BINARY']

						# default to non-destructive rename mode
						overwrite = False

						try:
							overwrite = activity['OVERWRITE']
						except Exception:
							pass

						if not overwrite:
							# look for duplicates
							i = 0
							while path.exists(target):
								i += 1
								target = 'files/' + ftarget + " (" + str(i) + ")"+ fext

						s.fmod_write(target, data, 'w', binary)

					elif (action == 'APPEND'):
						data = activity['DATA']
						binary = activity['BINARY']

						if not binary:
							try:
								data += ('', '\n')[activity['BREAK']]
							except Exception:
								pass

						s.fmod_write(target, data, 'a', binary)

					elif (action == 'REMOVE'):
						pass

				else:
					raise Exception

		except Exception as e:
			print("ERROR: " + str(e))
			s.send_response(status.BAD_REQUEST)
			s.end_headers()
			return

		print(sender + " - " + sender_hostname + " - " + src_type + " - " + str(content_length) + " BYTES - OK")

		s.send_response(status.ACCEPTED)
		s.end_headers()
		return

	def fmod_write(s, file, data, write_mode = 'a', binary = False):
		if binary:
			write_mode += 'b'

		try:
			f = open(file, write_mode)

			if binary:
				# convert to bytes then decode
				b = bytes(data, 'utf-8')
				f.write(base64.urlsafe_b64decode(b))

			else:
				f.write(data)

			f.close()

		except Exception as e:
			raise e



if __name__ == '__main__':
	main()