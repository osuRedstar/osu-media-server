from time import localtime, strftime

#bcolors
"""Console colors"""
PINK 		= '\033[95m'
BLUE 		= '\033[94m'
GREEN 		= '\033[92m'
YELLOW 		= '\033[93m'
RED 		= '\033[91m'
ENDC 		= '\033[0m'
BOLD 		= '\033[1m'
UNDERLINE 	= '\033[4m'

def getTimestamp():
	"""
	Return current time in YYYY-MM-DD HH:MM:SS format.
	Used in logs.

	:return: readable timestamp
	"""
	return strftime("%Y-%m-%d %H:%M:%S", localtime())

def logMessage(message, alertType = "INFO", messageColor = ENDC, discord = None, alertDev = False, of = None, stdout = True):
	"""
	Log a message

	:param message: message to log
	:param alertType: alert type string. Can be INFO, WARNING, ERROR or DEBUG. Default: INFO
	:param messageColor: message console ANSI color. Default: no color
	:param discord: Discord channel acronym for Schiavo. If None, don't log to Discord. Default: None
	:param alertDev: 	if True, developers will be highlighted on Discord.
						Obviously works only if the message will be logged to Discord.
						Default: False
	:param of:	Output file name (inside .data folder). If None, don't log to file. Default: None
	:param stdout: If True, log to stdout (print). Default: True
	:return:
	"""
	# Get type color from alertType
	if alertType == "INFO":
		typeColor = GREEN
	elif alertType == "WARNING":
		typeColor = YELLOW
	elif alertType == "ERROR":
		typeColor = RED
	elif alertType == "CHAT":
		typeColor = BLUE
	elif alertType == "DEBUG":
		typeColor = PINK
	else:
		typeColor = ENDC

	# Message without colors
	finalMessage = "[{time}] {type} - {message}".format(time=getTimestamp(), type=alertType, message=message)

	# Message with colors
	finalMessageConsole = "{typeColor}[{time}] {type}{endc} - {messageColor}{message}{endc}".format(
		time=getTimestamp(),
		type=alertType,
		message=message,

		typeColor=typeColor,
		messageColor=messageColor,
		endc=ENDC
	)

	# Log to console
	if stdout: print(finalMessageConsole)

	if isLog:
		with open("logs.txt", "a", encoding="utf-8") as f: f.write(f"{finalMessageConsole}\n")

def warning(message, discord = None, alertDev = False):
	"""
	Log a warning to stdout and optionally to Discord

	:param message: warning message
	:param discord: Discord channel acronym for Schiavo. If None, don't log to Discord. Default: None
	:param alertDev: 	if True, developers will be highlighted on Discord.
						Obviously works only if the message will be logged to Discord.
						Default: False
	:return:
	"""
	logMessage(message, "WARNING", YELLOW, discord, alertDev)

def error(message, discord = None, alertDev = True):
	"""
	Log a warning message to stdout and optionally to Discord

	:param message: warning message
	:param discord: Discord channel acronym for Schiavo. If None, don't log to Discord. Default: None
	:param alertDev: 	if True, developers will be highlighted on Discord.
						Obviously works only if the message will be logged to Discord.
						Default: False
	:return:
	"""
	logMessage(message, "ERROR", RED, discord, alertDev)

def info(message, discord = None, alertDev = False):
	"""
	Log an info message to stdout and optionally to Discord

	:param message: info message
	:param discord: Discord channel acronym for Schiavo. If None, don't log to Discord. Default: None
	:param alertDev: 	if True, developers will be highlighted on Discord.
						Obviously works only if the message will be logged to Discord.
						Default: False
	:return:
	"""
	logMessage(message, "INFO", ENDC, discord, alertDev)

def debug(message):
	"""
	Log a debug message to stdout.
	Works only if the server is running in debug mode.

	:param message: debug message
	:return:
	"""
	"""
	if glob.debug:	#glob.debug == False
		logMessage(message, "DEBUG", PINK)
	"""
	if True:
		logMessage(message, "DEBUG", PINK)

def chat(message):
	"""
	Log a public chat message to stdout and to chatlog_public.txt.

	:param message: message content
	:return:
	"""
	logMessage(message, "CHAT", BLUE, of="chatlog_public.txt")

try:
	with open("config.ini", "r") as f: #isLog
		isLog = f.read()
		isLog = True if isLog[isLog.find("islog"):].split("\n")[0].replace("islog = ", "") == "True" else False
		if isLog: chat("logs.txt 활성화")
		else: warning("logs.txt 비활성화")
except: isLog = False