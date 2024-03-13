import re, time, os, sys

file_path = sys.argv[1]

with open(file_path, "r") as file:
	lines = file.readlines()

pattern = re.compile(r'(version = ")([0-9]+\.[0-9]+\.)([0-9]+)(")')
version = ""

current_time = time.time()
last_modified_time = os.path.getmtime(file_path)
last_modified_min_ago = (current_time - last_modified_time) / 60

with open(file_path, "w") as file:
	for line in lines:
		match = pattern.search(line)

		line_to_write = line
		if match:
			major_minor = match.group(2)
			patch = int(match.group(3))
			if last_modified_min_ago > 5:
				version = f"{major_minor}{patch+1}"
			else:
				version = f"{major_minor}{patch}"  # leaves as is
			# print(f"Version: {version}")
			line_to_write = f'version = "{version}"\n'

		file.write(line)

assert version != ""
print(version)
