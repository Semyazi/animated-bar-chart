COMMENT_BLACKLIST = ["http", "mod edit", "mod note", "verifier edit", "verifier note"]

def preprocess_comment(comment):
	comment_segments = []
	
	for line in comment.splitlines():
		lowercase_line = line.lower()
		includes_blacklisted_phrase = False

		for phrase in COMMENT_BLACKLIST:
			if phrase in lowercase_line:
				includes_blacklisted_phrase = True				
				break

		if not includes_blacklisted_phrase and len(line) > 0:
			comment_segments.append(line)

	return " ".join(comment_segments)