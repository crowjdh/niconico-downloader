import argparse

rangeFormatHelp = 'startIdx:count'
defaultProcessesCount = 2

def rangeFilter(r):
	args = r.split(':')
	if len(args) == 2:
		return args
	else:
		raise argparse.ArgumentTypeError('Must be in form of {0}'.format(rangeFormatHelp))

def parse():
	parser = argparse.ArgumentParser(description='Niconico douga downloader')
	# parser.add_argument('-email', action="store_true", default=False)
	parser.add_argument('email', help='E-mail ID')
	parser.add_argument('password', help='Password')
	parser.add_argument('-o', dest='outputPath', help='Output path')
	parser.add_argument('-p', '--processes', help='Concurrent processes count(default: {0})'.format(defaultProcessesCount), default=defaultProcessesCount, type=int)

	subparsers = parser.add_subparsers(help='Mode')

	videoParser = subparsers.add_parser('v', help='Video ID mode')
	videoParser.add_argument('videoId', nargs='+', help='Video ID to download')
	videoParser.set_defaults(mode='v')

	myListParser = subparsers.add_parser('m', help='MyList mode')
	myListParser.add_argument('mylistId', help='MyList ID to download')
	myListParser.add_argument('-r', dest='range', help='Range in list(in form of {0})'.format(rangeFormatHelp), type=rangeFilter)
	myListParser.add_argument('-s', dest='sort', help='Sort list(-1 for reversed order)', action='store_false')
	myListParser.set_defaults(mode='m')

	return parser.parse_args()
	
