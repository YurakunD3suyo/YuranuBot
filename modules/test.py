import re
import emoji



ignore = r':\S+\:'

sentence = "🙃"

sentence = emoji.demojize(sentence)

print(re.sub(ignore, "絵文字", sentence, flags=re.IGNORECASE))