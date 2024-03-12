import re

file_path = "pyproject.toml"

with open(file_path, "r") as file:
	lines = file.readlines()

pattern = re.compile(r'(version = ")([0-9]+\.[0-9]+\.)([0-9]+)(")')

with open(file_path, "w") as file:
	for line in lines:
		match = pattern.search(line)
		if match:
			major_minor = match.group(2)
			patch = int(match.group(3)) + 1
			new_version_line = f'version = "{major_minor}{patch}"\n'
			file.write(new_version_line)
		else:
			file.write(line)
