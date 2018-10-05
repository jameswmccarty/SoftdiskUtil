#!/usr/bin/python

# Softdisk Text Decompress Utility
# Reconstruct a CTX compressed file
# For information on format, see:
# http://fileformats.archiveteam.org/wiki/Softdisk_Text_Compressor

import sys

if __name__ == "__main__":

	if len(sys.argv) < 2:
		print("Provide input file name.")
		exit()

	outname = '' # original file name
	s_seqs = []  # low byte value compression sequences table (29 total)
	d_seqs = []  # high byte value compression sequences table (127 total)

	with open(sys.argv[1], "rb") as f:
		header = f.read(6)
		print header
		if header != '\x03\x43\x54\x30\x30\x31': # magic number "Control-C followed by CT001"
			print("Invalid file header.")
			exit()
		while True: # read NULL terminated file name
			byte = f.read(1)
			if byte == '\x00': # reached end of file name
				break
			outname += byte
		if outname == '':
			print("Got empty file name.")
			exit()
		print("Got file name: " + outname)

		for i in range(0,30): # read 29 sequences of 5 char (or NULL terminated) strings
			sub = ''
			while True:		
				byte = f.read(1)
				if byte == '\x00' or len(sub) == 5: # or NULL terminated if shorter
					break
				sub += byte
			s_seqs.append(sub)

		for i in range(0,128): # read 127 2-character sequences
			d_seqs.append(f.read(2))

		# tables built.  now at the data portion.

		print("Tables built.")

		print(s_seqs)
		print(d_seqs)

		print("Decoding file...")

		with open(outname, "wb") as o:
			while True:
				byte = f.read(1)
				if byte is None or len(byte) == 0:
					break # reached EOF
				if '\x20' <= byte <= '\x7f':
					o.write(byte)
				elif byte == '\x0d': # CR outputs Line Break
					o.write('\x0d\x0a') # CRLF
				elif '\x00' <= byte <= '\x09': 
					o.write(s_seqs[ord(byte)])
				elif '\x0b' <= byte <= '\x0c':
					o.write(s_seqs[ord(byte)-1])
				elif '\x0e' <= byte <= '\x1F':
					o.write(s_seqs[ord(byte)-2])
				elif '\x80' <= byte <= '\xfe':
					o.write(d_seqs[ord(byte)-128])
				elif byte == '\xff':
					next = f.read(1)
					if '\x20' <= next <= '\x7f':
						n = ord(next) - 30
						c = f.read(1)
						for r in range(n):
							o.write(c)
					else:
						o.write(next)

	o.close()
	f.close()
	print("Done.")
			
