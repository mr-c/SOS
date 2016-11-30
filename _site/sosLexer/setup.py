from setuptools import setup, find_packages
 
setup (
	name='soslexer',
	packages=find_packages(),
	entry_points =
	"""
		[pygments.lexers]
		soslexer = soslexer.lexer:sosLexer
	""",
	)
