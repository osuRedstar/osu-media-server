import os
import configparser

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

		try:
			# Try to get all the required keys
			self.config.get("server","port")
			self.config.get("server","flaskdebug")

			self.config.get("osu","APIKEY")
			self.config.get("osu","IS_YOU_HAVE_OSU_PRIVATE_SERVER_WITH_lets.py")
			return True
		except:
			return False


	# Generate a default config.ini
	def generateDefaultConfig(self):
		"""Open and set default keys for that config file"""

		# Open config.ini in write mode
		f = open(self.fileName, "w")

		# Set keys to config object
		self.config.add_section("server")
		self.config.set("server", "port", "6200")
		self.config.set("server", "flaskdebug", "0")

		self.config.add_section("osu")
		self.config.set("osu", "APIKEY", "Your_OSU_APIKEY")
		self.config.set("osu", "IS_YOU_HAVE_OSU_PRIVATE_SERVER_WITH_lets.py", "True")

		# Write ini to file and close
		self.config.write(f)
		f.close()