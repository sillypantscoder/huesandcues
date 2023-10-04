import os
import math
import random
from urllib.parse import unquote

class GameStatus:
	WAIT_TO_BEGIN = 0
	WAIT_FOR_CLUE = 1
	WAIT_FOR_PLAYER_GUESS = 2
	SHOW_RESULTS = 3

def read_file(filename):
	f = open(filename, "r")
	t = f.read()
	f.close()
	return t

def bin_read_file(filename):
	f = open(filename, "rb")
	t = f.read()
	f.close()
	return t

def write_file(filename, content):
	f = open(filename, "w")
	f.write(content)
	f.close()

pwd = ''.join([random.choice([*"ABCDEFGHIKLMNPQRSTUVWXYZ0123456789"]) for x in range(4)])
pending = []

class Game:
	def __init__(self):
		self.status = GameStatus.WAIT_TO_BEGIN
		self.cluer = None
		self.players = []
		self.clue = None
		self.guesses = []
		self.score = []
		self.done = []
	def get(self, path):
		if path == "/status_" + pwd:
			return {
				"status": 200,
				"headers": {
					"Content-Type": "text/html"
				},
				"content": """<!DOCTYPE html>
<html>
	<head>
		<title>Game Status</title>
	</head>
	<body>
		<h1>Game Status</h1>
		<div style="font-family: monospace; white-space: pre;" id="t"></div>
		<div><input type="text" enterheyhint="send" onkeydown="if (event.key == 'Enter') sendMsg(this.value)"><button onclick="sendMsg(this.previousElementSibling.value)">Send</button></div>
		<script>
setInterval(() => {
	var x = new XMLHttpRequest()
	x.open("GET", location.pathname + "/s/")
	x.addEventListener("loadend", (e) => {
		document.querySelector("#t").innerText = e.target.responseText
	})
	x.send()
}, 1000)
function sendMsg(t) {
	var x = new XMLHttpRequest()
	x.open("GET", location.pathname + "/s/" + t)
	x.send()
	document.querySelector("input").value = ""
}
		</script>
	</body>
</html>"""
			}
		elif path.startswith("/status_" + pwd + "/s/"):
			d = path[len("/status_" + pwd + "/s/"):]
			return {
				"status": 200,
				"headers": {
					"Content-Type": "text/plain"
				},
				"content": self.get_status(unquote(d))
			}
		if os.path.isfile(os.path.join("public_files", path[1:])):
			return {
				"status": 200,
				"headers": {
					"Content-Type": "text/html"
				},
				"content": bin_read_file(os.path.join("public_files", path[1:]))
			}
		elif path == "/":
			return {
				"status": 200,
				"headers": {
					"Content-Type": "text/html"
				},
				"content": read_file("assets/enter_name.html")
			}
		elif path.split("?")[0] == "/game/main":
			# Start new game?
			if len(self.players) >= 2 and self.status == GameStatus.WAIT_TO_BEGIN:
				self.cluer = random.choice(self.players)
				self.status = GameStatus.WAIT_FOR_CLUE
				self.msg(f"Cluer is: {unquote(self.cluer)} (out of {self.players})")
				self.clue = [[random.randint(0, 800), random.randint(0, 480)] for zzz in range(3)]
			# Main
			playername = ''.join(path.split("?")[1:])[5:]
			if playername not in self.players:
				if playername not in pending: pending.append(playername)
				return {
					"status": 200,
					"headers": {
						"Content-Type": "text/html"
					},
					"content": read_file("assets/admit.html")
				}
			if self.status == GameStatus.WAIT_TO_BEGIN:
				# WAITING TO BEGIN
				return {
					"status": 200,
					"headers": {
						"Content-Type": "text/html"
					},
					"content": read_file("assets/wait_begin.html")
				}
			if self.status == GameStatus.WAIT_FOR_CLUE:
				# WAITING FOR THE CLUE
				if playername == self.cluer:
					return {
						"status": 200,
						"headers": {
							"Content-Type": "text/html"
						},
						"content": read_file("assets/give_clue.html").replace("{{INSERT COLOR OPTIONS HERE}}", f"{self.clue}")
					}
				else:
					return {
						"status": 200,
						"headers": {
							"Content-Type": "text/html"
						},
						"content": read_file("assets/wait_clue.html").replace("{{INSERT CLUE GIVER HERE}}", unquote(self.cluer))
					}
			if self.status == GameStatus.WAIT_FOR_PLAYER_GUESS and not playername == self.cluer:
				# WAITING FOR THE PLAYERS' GUESSES
				return {
					"status": 200,
					"headers": {
						"Content-Type": "text/html"
					},
					"content": read_file("assets/guess.html").replace("{{INSERT CLUE HERE}}", self.clue.split("\n")[2]).replace("{{INSERT NAME HERE}}", playername)
				}
			if self.status == GameStatus.SHOW_RESULTS or (self.status == GameStatus.WAIT_FOR_PLAYER_GUESS and playername == self.cluer):
				# SHOWING THE RESULTS
				if self.status == GameStatus.SHOW_RESULTS and self.done[self.players.index(playername)]: return {
					"status": 200,
					"headers": {
						"Content-Type": "text/html"
					},
					"content": read_file("assets/wait_finish.html")
				}
				# Assemble content
				content = read_file("assets/wait_guess.html")\
					.replace("{{INSERT CLUE HERE}}", self.clue.split("\n")[2])\
					.replace("// INSERT RESULT HERE", f"[{self.clue.splitlines()[0]}, {self.clue.splitlines()[1]}]")\
					.replace("{{INSERT PLAYER NAME HERE}}", playername)
				return {
					"status": 200,
					"headers": {
						"Content-Type": "text/html"
					},
					"content": content
				}
		elif path.split("?")[0] == "/game/wait_guesses":
			playername = ''.join(path.split("?")[1:])[5:]
			if self.status != GameStatus.WAIT_FOR_PLAYER_GUESS:
				return {
					"status": 303,
					"headers": {
						"Location": "/game/main?name=" + playername
					},
					"content": f""
				}
			return {
				"status": 200,
				"headers": {
					"Content-Type": "text/html"
				},
				"content": read_file("assets/wait_guess.html")\
					.replace("{{INSERT CLUE HERE}}", self.clue.split("\n")[2])\
					.replace("{{INSERT GUESSES HERE}}", ''.join([f"<div style='position: absolute; --y: {self.guesses[i][1]}px; left: {self.guesses[i][0]}px;'>{self.players[i]}</div>" for i in range(len(self.players)) if self.guesses[i] != None]))
			}
		elif path.split("?")[0] == "/getscore":
			playername = ''.join(path.split("?")[1:])[5:]
			try:
				return {
					"status": 200,
					"headers": {
						"Content-Type": "text/plain"
					},
					"content": str(self.score[self.players.index(playername)])
				}
			except:
				return {
					"status": 500,
					"headers": {
						"Content-Type": "text/plain"
					},
					"content": "Not logged in"
				}
		elif path.split("?")[0] == "/game/get_guesses":
			playerinfo = []
			for i in range(len(self.players)):
				if self.guesses[i] != None:
					playerinfo.append(f"<div style='--y: {self.guesses[i][1]}px; left: {self.guesses[i][0]}px;'>{unquote(self.players[i])}</div>")
			return {
				"status": 200,
				"headers": {
					"Content-Type": "text/html"
				},
				"content": ''.join(playerinfo) if self.status != GameStatus.SHOW_RESULTS else "RELOAD"
			}
		elif path.split("?")[0] == "/game/get_guesses_final":
			playerinfo = []
			for i in range(len(self.players)):
				if self.guesses[i] != None:
					playerdist = math.dist((float(self.guesses[i][0]), float(self.guesses[i][1])), (float(self.clue.splitlines()[0]), float(self.clue.splitlines()[1])))
					displayname = self.players[i]
					if playerdist < 40: displayname += ' +1.5'
					elif playerdist < 100: displayname += ' +0.5'
					playerinfo.append(f"<div style='--y: {self.guesses[i][1]}px; left: {self.guesses[i][0]}px;'>{unquote(displayname)}</div>")
			return {
				"status": 200,
				"headers": {
					"Content-Type": "text/html"
				},
				"content": ''.join(playerinfo)
			}
		else: # 404 page
			print("Invalid GET to " + path)
			return {
				"status": 404,
				"headers": {
					"Content-Type": "text/html"
				},
				"content": f""
			}
	def post(self, path, body):
		if path == "/submitclue":
			self.clue = body.decode("UTF-8")
			self.status = GameStatus.WAIT_FOR_PLAYER_GUESS
			self.msg("Clue is: " + self.clue.replace("\n", " "))
			return {
				"status": 200,
				"headers": {},
				"content": f""
			}
		elif path == "/submitguess":
			b = body.decode("UTF-8").split("\n")
			self.guesses[self.players.index(b[0])] = [b[1], b[2]]
			self.msg(f"{unquote(b[0])} guessed: {b[1]}, {b[2]}")
			if self.guesses.count(None) <= 1:
				self.status = GameStatus.SHOW_RESULTS
				self.msg(f"Everyone's done guessing!")
				self.done = [False for x in self.done]
			return {
				"status": 200,
				"headers": {},
				"content": f""
			}
		elif path == "/clear":
			try:
				self.done[self.players.index(body.decode('UTF-8'))] = True
			except: print("FAILED")
			self.msg(f"{unquote(body.decode('UTF-8'))} is done")
			if self.status == GameStatus.SHOW_RESULTS:
				if False not in [x == True for x in self.done]:
					self.msg(f"Everyone's finished! Updating scoreboard...")
					o_score = [*self.score]
					for i in range(len(self.players)):
						if self.players[i] == self.cluer: continue
						acc = math.dist((int(self.guesses[i][0]), int(self.guesses[i][1])), (int(self.clue.splitlines()[0]), int(self.clue.splitlines()[1])))
						if acc < 40:
							self.score[i] += 1.5
							self.score[self.players.index(self.cluer)] += 0.8
						elif acc < 100:
							self.score[i] += 0.5
							self.score[self.players.index(self.cluer)] += 0.2
						else:
							self.score[self.players.index(self.cluer)] -= 0.1
					# Print results
					print("\n--- SCORES ---")
					for i in range(len(self.players)):
						print(f" {unquote(self.players[i])}: {o_score[i]} + {self.score[i] - o_score[i]} = {self.score[i]}")
					# Reset
					self.status = GameStatus.WAIT_TO_BEGIN
					self.guesses = [None for x in self.guesses]
					self.cluer = None
					print("\n\n")
			return {
				"status": 200,
				"headers": {},
				"content": f""
			}
		else:
			print("Invalid POST to " + path)
			return {
				"status": 404,
				"headers": {
					"Content-Type": "text/html"
				},
				"content": f""
			}
	def msg(self, message):
		bars = 0
		maxbars = 3
		if self.status == GameStatus.WAIT_FOR_CLUE: bars += 1
		if self.status == GameStatus.WAIT_FOR_PLAYER_GUESS: bars += 2
		if self.status == GameStatus.SHOW_RESULTS:
			maxbars -= 3
			for p in range(len(self.players)):
				maxbars += 1
				if self.done[p]: bars += 1
		else:
			for p in range(len(self.players)):
				if self.players[p] == self.cluer:
					continue
				maxbars += 1
				if self.guesses[p] != None: bars += 1
		bar = ("=" * bars).ljust(maxbars, ' ')
		print(f"- [{bar}] {message}")
	def get_status(self, inkey):
		r = ""
		# Status
		r += f"Status: {['Waiting to begin', 'Waiting for a clue', 'Waiting for player guesses', 'Showing the results'][self.status]}\n"
		# Player list
		r += f"Players:\n"
		for i in range(len(self.players)):
			r += f"\t- (r{i}) {self.players[i]}"
			if self.players[i] == self.cluer:
				if self.status == GameStatus.WAIT_FOR_CLUE: r += f" [CLUE OPTIONS: {', '.join([f'({x[0]}, {x[1]})' for x in self.clue])}]"
				else:
					c = self.clue.split("\n")
					r += f" [CLUE: ({c[0]}, {c[1]}) -> {repr(c[2])}]"
			r += f" [score: {self.score[i]}]"
			if self.guesses[i]: r += f" [guess: ({int(self.guesses[i][0])}, {int(self.guesses[i][1])})]"
			if self.done[i]: r += f" [done!]"
			r += "\n"
			if inkey == f"r{i}":
				# goodbye :/
				del self.players[i]
				del self.guesses[i]
				del self.score[i]
				del self.done[i]
				return "deleted player!"
		# Pending player list:
		r += "\nPending players:\n"
		for i in range(len(pending)):
			playername = pending[i]
			r += f"\t- (a/d {i}) {playername}\n"
			if inkey == f"a{i}":
				inkey = f"d{i}"
				self.players.append(playername)
				self.guesses.append(None)
				self.score.append(0.0)
				self.done.append(False)
				self.msg(f"Added player: {unquote(playername)}")
			if inkey == f"d{i}":
				pending.remove(playername)
		# Other info
		r += "\n(m <name>) Manually add player\n"
		if inkey.startswith("m"):
			playername = inkey[1:]
			self.players.append(playername)
			self.guesses.append(None)
			self.score.append(0.0)
			self.done.append(False)
			self.msg(f"Added player: {unquote(playername)}")
		r += "(s<player> <name>=<value>, ...) Set player data"
		if inkey.startswith("s"):
			playeri = int(inkey.split(" ")[0][1:])
			data = ' '.join(inkey.split(" ")[1:]).split(", ")
			for d in data:
				name = d.split("=")[0]
				value = d.split("=")[1]
				if name == "score": self.score[playeri] = float(value)
				if name == "done": self.done[playeri] = value == "true"
		# Finish
		return r