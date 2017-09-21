# -*- coding: UTF-8 -*-

import MySQLdb
import sys

__all__ = ['MySQL']
class MySQL(object):
	conn = ''
	cursor = ''
	def __init__(self,host='localhost',port=3306,user='root',passwd='root',db='mysql',charset='utf8'):
		self.host = host
		self.port = port
		self.user = user
		self.passwd = passwd
		self.db = db
		try:
			self.conn = MySQLdb.connect(host=self.host,user=self.user,passwd=self.passwd,db=self.db)
		except MySQLdb.Error,e:
			errormsg = 'Cannot connect to server\nERROR (%s): %s' %(e.args[0],e.args[1])
			print errormsg
			sys.exit()
		
		self.cursor = self.conn.cursor()

	def execute(self, sql):
		"""  Execute SQL statement """
		return self.cursor.execute(sql)

	def show(self):
		""" Return the results after executing SQL statement """
		return self.cursor.fetchall()

	def __del__(self):
		""" Terminate the connection """
		print "close"
		self.conn.close()
		self.cursor.close()

