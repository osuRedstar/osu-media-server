import os
import configparser
from helpers import logUtils as log

class config:
	"""
	config.ini object

	config -- list with ini data
	default -- if true, we have generated a default config.ini
	"""

	config = configparser.ConfigParser()
	extra = {}
	fileName = ""		# config filename
	default = True

	# Check if config.ini exists and load/generate it
	def __init__(self, __file):
		"""
		Initialize a config object

		__file -- filename
		"""

		self.fileName = __file
		if os.path.isfile(self.fileName):
			# config.ini found, load it
			self.config.read(self.fileName)
			self.default = False
		else:
			# config.ini not found, generate a default one
			self.generateDefaultConfig()
			self.default = True

	# Check if config.ini has all needed the keys
	def checkConfig(self):
		"""
		Check if this config has the required keys

		return -- True if valid, False if not
		"""

		noneCheck = []

		try:
			# Try to get all the required keys
			noneCheck.append(self.config.get("server","port"))
			noneCheck.append(self.config.get("server","flaskdebug"))
			noneCheck.append(self.config.get("server","islog"))
			noneCheck.append(self.config.get("server","AllowedConnentedBot"))
			noneCheck.append(self.config.get("server","dataFolder"))
			noneCheck.append(self.config.get("server","oszRenewTime"))
			noneCheck.append(self.config.get("server","removekey"))
			noneCheck.append(self.config.get("server","osuServerDomain"))
			noneCheck.append(self.config.get("server","ContectEmail"))

			noneCheck.append(self.config.get("osu","Bancho_Apikeys"))
			noneCheck.append(self.config.get("osu","Bancho_username"))
			noneCheck.append(self.config.get("osu","Bancho_password"))
			noneCheck.append(self.config.get("osu","IS_YOU_HAVE_OSU_PRIVATE_SERVER_WITH_lets.py"))
			noneCheck.append(self.config.get("osu","lets.py_beatmaps_Folder_Path"))

			noneCheck.append(self.config.get("db","host"))
			noneCheck.append(self.config.get("db","port"))
			noneCheck.append(self.config.get("db","username"))
			noneCheck.append(self.config.get("db","password"))
			noneCheck.append(self.config.get("db","database"))

			noneCheck.append(self.config.get("mmdb","id"))
			noneCheck.append(self.config.get("mmdb","key"))
			return True
		except:
			return False
		finally:
			if None in noneCheck or "" in noneCheck:
				return None
				


	# Generate a default config.ini
	def generateDefaultConfig(self):
		"""Open and set default keys for that config file"""

		# Open config.ini in write mode
		f = open(self.fileName, "w")

		# Set keys to config object
		self.config.add_section("server")
		self.config.set("server", "port", "6200")
		self.config.set("server", "flaskdebug", "0")
		self.config.set("server", "islog", "True")
		self.config.set("server", "AllowedConnentedBot", "False")
		self.config.set("server", "dataFolder", "data")
		self.config.set("server", "oszRenewTime", "604800")
		self.config.set("server", "removekey", "")
		self.config.set("server", "osuServerDomain", "redstar.moe")
		self.config.set("server", "ContectEmail", "support@redstar.moe")

		self.config.add_section("osu")
		self.config.set("osu", "Bancho_Apikeys", "['Your_Bancho_APIKKEY_1', 'Your_Bancho_APIKKEY_2']")
		self.config.set("osu", "Bancho_username", "")
		self.config.set("osu", "Bancho_password", "")
		self.config.set("osu", "IS_YOU_HAVE_OSU_PRIVATE_SERVER_WITH_lets.py", "False")
		if os.name == "nt":
			self.config.set("osu", "lets.py_beatmaps_Folder_Path", "B:/redstar/lets/.data/beatmaps")
		else:
			self.config.set("osu", "lets.py_beatmaps_Folder_Path", "/home/{user}/redstar/lets/.data/beatmaps")

		self.config.add_section("db")
		self.config.set("db", "host", "localhost")
		self.config.set("db", "port", "3306")
		self.config.set("db", "username", "root")
		self.config.set("db", "password", "")
		self.config.set("db", "database", "redstar")

		self.config.add_section("mmdb")
		self.config.set("mmdb", "id", "")
		self.config.set("mmdb", "key", "")

		# Write ini to file and close
		self.config.write(f)
		f.close()

conf = config("config.ini")

if conf.default:
	# We have generated a default config.ini, quit server
	log.warning("[!] config.ini not found. A default one has been generated.")
	log.warning("[!] Please edit your config.ini and run the server again.")
	exit()

# If we haven't generated a default config.ini, check if it's valid
if conf.checkConfig() is None:
	log.warning("[!] There are omissions in some setting values.")
	log.warning("[!] Please edit your config.ini and run the server again.")
	exit()
elif not conf.checkConfig():
	log.error("[!] Invalid config.ini. Please configure it properly")
	log.error("[!] Delete your config.ini to generate a default one")
	exit()