import os
import math
import random

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
				self.msg(f"Cluer is: {self.cluer} (out of {self.players})")
				self.clue = [[random.randint(0, 800), random.randint(0, 480)] for zzz in range(3)]
			# Main
			playername = ''.join(path.split("?")[1:])[5:]
			if playername not in self.players:
				self.players.append(playername)
				self.guesses.append(None)
				self.score.append(0.0)
				self.done.append(False)
				self.msg(f"Added player: {playername}")
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
						"content": read_file("assets/wait_clue.html").replace("{{INSERT CLUE GIVER HERE}}", self.cluer)
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
				playerinfo = []
				for i in range(len(self.players)):
					if self.guesses[i] != None:
						playerdist = math.dist((int(self.guesses[i][0]), int(self.guesses[i][1])), (int(self.clue.splitlines()[0]), int(self.clue.splitlines()[1])))
						displayname = self.players[i]
						if playerdist < 40: displayname += ' +1.5'
						elif playerdist < 100: displayname += ' +0.5'
						playerinfo.append(f"<div style='--y: {self.guesses[i][1]}px; left: {self.guesses[i][0]}px;'>{displayname}</div>")
				# Assemble content
				content = read_file("assets/wait_guess.html")\
					.replace("{{INSERT CLUE HERE}}", self.clue.split("\n")[2])\
					.replace("{{INSERT GUESSES HERE}}", ''.join(playerinfo))\
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
			return {
				"status": 200,
				"headers": {
					"Content-Type": "text/plain"
				},
				"content": str(self.score[self.players.index(playername)])
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
			self.msg(f"{b[0]} guessed: {b[1]}, {b[2]}")
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
			self.done[self.players.index(body.decode('UTF-8'))] = True
			self.msg(f"{body.decode('UTF-8')} is done")
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
						print(f" {self.players[i]}: {o_score[i]} + {self.score[i] - o_score[i]} = {self.score[i]}")
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