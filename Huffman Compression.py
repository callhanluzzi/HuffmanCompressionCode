# Adam Lavoie, Callhan Luzzi
2# Professor Daniels
3# CSC 440
4# October 28th, 2016
5
6import os
7import sys
8import marshal
9from array import array
10import operator
11
12try:
13    import cPickle as pickle
14except:
15    import pickle
16
17#create an array for the leaves of the tree, and the dict that will hold the codes for each character
18leaves = []
19codes = {}
20
21#helper method to generate huffman codes for a character based on its path in the tree
22def genHuff(ch,t,path):
23	#if we have reached the end of the tree, return the path
24	if ch == t:
25
26		return path
27	else:
28        #if not, then we step through to find the corresponding huff encoding
29		if not(t[0] == t):
30			return genHuff(ch,t[0],path + "0") + genHuff(ch,t[1],path + "1")
31	return ""
32    
33		
34#helper method to create our tree based on the frequency of the characters	
35def freqstotree(freqs):
36	
37	if freqs in leaves:
38		return freqs[1]
39	else:
40		return (freqstotree(freqs[1][0]),freqstotree(freqs[1][1]))
41	    
42
43#helper method to determine how many of each character is in the file
44def frequency(msg):
45	freqs = {}
46	for ch in msg:
47		freqs[ch] = freqs.get(ch,0) +1
48	f = []
49	for key in freqs:
50		f.append((freqs[key],key))
51		leaves.append((freqs[key],key))
52
53	return f
54
55
56def code(msg):
57	#length of coded messege
58	length = 0
59
60	#find the frequency of each letter in the msg
61	freq = frequency(msg)
62	#INITIALIZATION INVARIANT The tree must be sorted by frequency
63	freq.sort(key = operator.itemgetter(0))
64	tree = []
65		
66	#MAINTENANCE INVARIANT: while the frequency tuple can still be combined, loop
67	while len(freq)>1:
68		#get the two lowest elements
69		n1 = freq.pop(0)
70		n2 = freq.pop(0)
71		nSum = n1[0]+n2[0]
72		freq.append((nSum,(n1,n2)))
73		#resort
74		freq.sort(key = operator.itemgetter(0))
75
76	#TERMINATION INVARIANT is that we will have a frequency tuple tree that can be converted into a heirarchial tree used to generate huffman codes
77
78	#convert the frequency tuple to nested tuples to represent a tree
79	tree = freqstotree(freq[0])
80
81	codedmsg = ""
82	path = ""
83	#gets the Huffman codes for each tuple
84	for l in leaves:
85		 codes[l[1]] = genHuff(l[1],tree,"")
86
87	#convert each letter in the messege to the huffman code
88	for ch in msg:
89		length += len(codes[ch])
90		codedmsg = codedmsg + codes[ch]
91	return (codedmsg , (codes,length))
92
93
94def decode(str, decoderRing):
95	huffmancodes,length = decoderRing
96	decodes = {}
97	#invert the huffman codes {a:1100} -> {1100:a}
98	for k in huffmancodes:
99		decodes[huffmancodes[k]] = k
100	
101	msg = ""
102	bits = ""
103	#greedy search the coded message and convert into letters
104	for b in str:
105		bits = bits+b
106		if bits in decodes:
107			msg = msg + decodes[bits]
108			bits = ""
109
110	return msg
111				
112
113def compress(msg):
114	#INITIALIZATION INVARIANT: We must have our Bcodes, this is ourhuffman codes, 1's and 0's, that must be converted into binary values
115	Bcodes, (codes,olength) = code(msg)
116	#create our bitstream of type unsigned int
117	bitstream = array('B')
118	#set our buffer value to 0, also set count to 0
119	buff = 0
120	c = 0
121	#set length to olength because we don't want to decrement olength to 0 and then return that value
122	length = olength
123
124	#TERMINATION INVARIANT: while a bit still exists in bcodes, loop
125	for bit in Bcodes:
126                #decrement length
127		length -= 1
128		#if bit is 0, shift left by 1
129		if bit == '0':
130			buff = (buff << 1)
131		#if bit is 1, shift left by 1 and OR with 1
132		if bit == '1':
133			buff = (buff << 1) | 1
134                #increment counter
135		c += 1
136		#MAINTENENCE INVARIANT: if c = 8, we know we have gone through 8 bits
137		#if length = 0, then we know we have hit the end of the string
138		#when either case is true, make changes to bitstream
139		if c == 8 or length == 0:
140                        #append buff to bitstream array
141			bitstream.append(buff)
142			#reset buff
143			buff = 0
144			#reset c so that we go through the string 8 bits at a time
145			c = 0
146	
147	return (bitstream, (codes,olength)) 
148
149
150def decompress(stri, decoderRing):
151
152	tree , length = decoderRing
153	#create a bitstream array of type unsigned int that takes in the original array from compress
154	#INITIALIZATION INVARIANT: We must have a bitstream to decompress
155	bitstream = array('B',stri)
156	#create msg
157	msg = ""
158	#MAINTENENCE INVARIANT: while any byte still exists in bitstream, loop
159    	for byte in bitstream:
160		m = ""
161		#set the buffer equal to our 8 bit byte
162		buff = byte
163		#MAINTENENCE INVARIANT: if lenght is > 0 make changes to string m
164		for i in range (0,8):
165			if not(length == 0):
166                                #AND buff with 1
167				b = (buff & 1)
168				#add that value to m
169				m = str(b) + m
170				#shift right by 1
171				buff = (buff >> 1)
172				#decrement length
173				length -= 1
174		#TERMINATION INVARIANT: if length reaches 0, end loop
175				
176		#add m to msg after finishing loop
177		msg = msg + m
178
179	#decode msg
180	#TERMINALTION INVARIANT: must have a binary msg and decorer tree to decode the huffman codes
181	original = decode(msg,decoderRing)
182	return original
183    		
184
185def usage():
186    sys.stderr.write("Usage: {} [-c|-d|-v|-w] infile outfile\n".format(sys.argv[0]))
187    exit(1)
188
189if __name__=='__main__':
190    if len(sys.argv) != 4:
191        usage()
192    opt = sys.argv[1]
193    compressing = False
194    decompressing = False
195    encoding = False
196    decoding = False
197    if opt == "-c":
198        compressing = True
199    elif opt == "-d":
200        decompressing = True
201    elif opt == "-v":
202        encoding = True
203    elif opt == "-w":
204        decoding = True
205    else:
206        usage()
207
208    infile = sys.argv[2]
209    outfile = sys.argv[3]
210    assert os.path.exists(infile)
211
212    if compressing or encoding:
213        fp = open(infile, 'rb')
214        str = fp.read()
215        fp.close()
216        if compressing:
217            msg, tree = compress(str)
218            fcompressed = open(outfile, 'wb')
219            marshal.dump((pickle.dumps(tree), msg), fcompressed)
220            fcompressed.close()
221        else:
222            msg, tree = code(str)
223            print(msg)
224            fcompressed = open(outfile, 'wb')
225            marshal.dump((pickle.dumps(tree), msg), fcompressed)
226            fcompressed.close()
227    else:
228        fp = open(infile, 'rb')
229        pickled_tree, msg = marshal.load(fp)
230        tree = pickle.loads(pickled_tree)
231        fp.close()
232        if decompressing:
233            str = decompress(msg, tree)
234        else:
235            str = decode(msg, tree)
236            print(str)
237        fp = open(outfile, 'wb')
238        fp.write(str)
239        fp.close()
