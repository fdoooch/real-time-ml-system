class TooManyRequestsToTradesSourceError(Exception):
	"""Raised when too many requests are made to the trades source."""

	def __init__(self, message="Too many requests to trades source."):
		super().__init__(message)
		self.message = message
