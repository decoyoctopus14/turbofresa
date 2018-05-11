#!/usr/bin/env python3
"""
    T.U.R.B.O.F.R.E.S.I.N.A
    Turboaggeggino Utile alla Rimorzione di Byte Obrobriosi e di abominevoli
    File da dischi rigidi Riciclati ed altri Elettronici Sistemi di
    Immagazzinamento (semi)permanente di dati Necessariamente Automatizzato.
    Copyright (C) 2018  Hyd3L

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import os
import sys
import datetime
import threading
import subprocess
import argparse  # @quel_tale will you finally stop smashing my nuts?
from getpass import getuser

__version__ = '1.1-RC3'

# Path of the log file
LOG_PATH = '/home/' + getuser() + '/.local/share/turbofresa/log.txt'

# Verbosity levels
ERROR, WARNING, INFO = range(0, 3)
VERBOSITY = INFO


def now():
	"""
		:return: a formatted string containing the current date and time
	"""
	return datetime.datetime.now().strftime('[%Y-%m-%d %H:%M:%S] ')


class Console(object):
	"""
		Class that handles the log file.
	"""
	def __init__(self):
		self.printLevel = VERBOSITY
		try:
			self.logFile = open(LOG_PATH, "a")
		except IOError:
			print("error: Permission denied. Log file couldn't be created.")
			sys.exit(34)

	def info(self, msg, to_std_out=False):
		if self.printLevel >= INFO:
			if to_std_out is True:
				print("info: " + msg)
			self.logFile.write(now() + "info: " + msg + '\n')

	def task(self, msg, to_std_out=False):
		if to_std_out is True:
			print("task: " + msg)
		self.logFile.write(now() + "task: " + msg + '\n')

	def warn(self, msg, to_std_out=False):
		if self.printLevel >= WARNING:
			if to_std_out is True:
				print("warning: " + msg)
			self.logFile.write(now() + "warning: " + msg + '\n')

	def error(self, msg, to_std_out=False):
		if self.printLevel >= ERROR:
			if to_std_out is True:
				print("error: " + msg)
			self.logFile.write(now() + "error: " + msg + '\n')

	def exit(self):
		self.logFile.close()


# Initialize log
log = Console()


def secure_exit(status=0):
	"""
		Safely quit the program, by closing the log file before quit.
		:param status: the exit code. (default = 0)
	"""
	log.exit()
	sys.exit(status)


def ask_confirm():
	"""
		Asks the user if (s)he is sure of what (s)he's doing.
	"""
	a = input("Are you 100% sure of what you're about to do? [N/y] ")
	if not (a == 'Y' or a == 'y'):
		log.info("User is a fa(ggot)int-hearted.")
		secure_exit()


def detect_os() -> str:
	"""
		Detects the hard drives connected to the machine
		:return: a list containing '/dev/sdX' entries
	"""
	os_disk = os.popen('df | grep /dev/sd | cut -b -8').read().split('\n')[0]
	return os_disk


def detect_disks() -> list:
	"""
		Detects the hard drives connected to the machine
		:return: a list containing '/dev/sdX' entries
	"""
	os_disk = detect_os()
	disks = list()
	lsblk = os.popen('lsblk | grep sd').read().split('\n')
	for line in lsblk:
		if line.startswith('s'):
			path = '/dev/'+line[:3]
			if path == os_disk:
				log.info("Skipping mounted drive: " + path, to_std_out=True)
				continue
			disks.append(path)
	return disks


class Task(threading.Thread):
	"""
		Class that handles the cleaning operation of a disk
	"""

	def __init__(self, hdd):
		"""
			:param hdd: A '/dev/sdX' formatted string
		"""
		threading.Thread.__init__(self)
		self.disk_path = hdd
		self.drive_name = hdd.split('/')[2]

	def run(self):
		"""
			This is the crucial part of the program.
			Here badblocks writes a stream of 0x00 bytes on the hard drive.
			After the writing process, it reads every blocks to ensure that they are actually 0x00 bytes.
			Bad blocks are eventually written in a txt file named as sdX.
			If this file is empty, then the disk is good to go, otherwise it'll be kept
			and the broken hard drive is reported into the log file.
		"""
		log.task("Started cleaning %s" % self.drive_name)
		subprocess.run(['sudo', 'badblocks', '-w', '-t', '0x00', '-o', self.drive_name, self.disk_path])
		result = os.popen('cat %s' % self.drive_name).read()
		if result == "":
			log.task("%s successfully cleaned.")
			subprocess.run(['rm', '-f', self.drive_name])
		else:
			log.task("%s is broken. Please, check the badblocks list.")


def main():
	parser = argparse.ArgumentParser(description='Automatically drill every single connected hard drive.')
	parser.add_argument('-s', '--shutdown', action='store_true', help='Shutdown the machine when everything is done.')
	parser.add_argument('-p', '--pretend', action='store_true', help='Pretend to be doing stuff.')
	parser.add_argument('--version', '-V', action='version', version='%(prog)s v.' + __version__)
	parser.set_defaults(shutdown=False)
	parser.set_defaults(pretend=False)
	args = parser.parse_args()

	ask_confirm()
	print("===> Detecting connected hard drives.")
	hdds = detect_disks()
	tasks = list()

	for d in hdds:
		tasks.append(Task(d))

	print("===> Cleaning disks")
	for t in tasks:
		if args.pretend is False:
			t.start()
		else:
			print("Started cleaning")

	for t in tasks:
		if args.pretend is False:
			t.join()
		else:
			print("Ended cleaning")

	if args.shutdown is True:
		if args.pretend is False:
			log.info("System halted by the user.")
			subprocess.run(['shutdown'])
		else:
			print("System halted.")
	print("Done.")


if __name__ == '__main__':
	main()
	secure_exit()
