from configparser import SafeConfigParser
import os
import praw
import datetime
import time
import re
import json
import sys
import logging

dir_path = os.path.dirname(os.path.realpath(__file__))

if not os.path.exists(dir_path + "\logs\\"):
    os.makedirs(dir_path + "\logs\\")

curr_log_date = datetime.datetime.now().strftime("%m-%d-%y")

logger = logging.getLogger("autoboot")
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler(dir_path + "\logs\\" + curr_log_date + ".log")
file_handler.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter("(%(asctime)s) %(levelname)s: %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)


def add_nonexistent(cfg, option, default="undefined", section="main"):
	if not cfg.has_option(section, option):
		cfg.set(section, option, default)

def add_nonexistent_section(cfg, section):
	if not cfg.has_section(section):
		cfg.add_section(section)

def init_config():
	cfg_path = dir_path + "\config.ini"

	config = SafeConfigParser()

	if not os.path.exists(cfg_path):
		open(cfg_path, "w").close()

		config.read(cfg_path)
	else:
		config.read(cfg_path)

	add_nonexistent_section(config, "main")

	add_nonexistent(config, "client_id")
	add_nonexistent(config, "client_secret")
	add_nonexistent(config, "password")
	add_nonexistent(config, "username")

	add_nonexistent_section(config, "limitations")
	add_nonexistent(config, "sub", "imaginedragonsteens", "limitations")

	with open(cfg_path, "w") as f:
		config.write(f)

	return config

# def log(string):
# 	print(datetime.datetime.now().strftime("(%m/%d/%y %H:%M:%S) AutoBoot: ") + string)

def praw_login(cfg):
	return praw.Reddit(client_id=cfg.get("main", "client_id"), client_secret=cfg.get("main", "client_secret"), password=cfg.get("main", "password"), user_agent='Auto Boot',username=cfg.get("main", "username"))

def construct_reply(body):
	return body

def find_word(w):
    return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search

config = init_config()
reddit = praw_login(config)

bottiquette = reddit.subreddit("bottiquette").wiki["robots_txt_json"]
bans = json.loads(bottiquette.content_md)

logger.info("Authenticated as Reddit user " + praw.models.User(reddit).me().name + ".")

run = True

subreddit = reddit.subreddit(config.get("limitations", "sub"))

bot_start_time = (datetime.datetime.utcnow() - datetime.datetime(1970,1,1)).total_seconds()

while run:
	logger.info("Analyzing new comments.")
	now_formatted = datetime.datetime.now().strftime("%m-%d-%y")
	if curr_log_date != now_formatted:
		logger.removeHandler(file_handler)
		curr_log_date = datetime.datetime.now().strftime("%m-%d-%y")
		file_handler = logging.FileHandler(dir_path + "\logs\\" + curr_log_date + ".log")
		formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
		file_handler.setFormatter(formatter)
		logger.addHandler(file_handler)

	for comment in subreddit.stream.comments():
		if ( find_word("boots")(comment.body) or find_word("boot")(comment.body) or find_word("b o o t s")(comment.body) ) and comment.created_utc >= bot_start_time and comment.subreddit.display_name.lower() not in bans["disallowed"]:
			comment.reply(construct_reply("#***W H E E Z E***"))
			logger.info("Replying to user " + comment.author.name + " on subreddit " + comment.subreddit.display_name)

	time.sleep(10)