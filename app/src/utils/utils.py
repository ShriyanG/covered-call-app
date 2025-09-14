from datetime import datetime


def format_date(dt):
	if not dt:
		return ''
	try:
		# Try parsing as datetime first
		d = datetime.strptime(dt, '%Y-%m-%d')
	except Exception:
		try:
			d = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
		except Exception:
			return str(dt)
	return d.strftime('%b %d, %Y')
