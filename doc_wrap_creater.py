dir_list = ["docs/atari", "docs/butterfly", "docs/classic", "docs/magent", "docs/mpe", "docs/sisl"]
output_dir = "environment_docs/"

import os

for dire in dir_list:
    new_dire = dire + "_doc/"
    for filename in os.listdir(dire):
        if filename.endswith(".md"):
            wrap_name = filename
            wrap_hand = open(wrap_name, "w")
            wrap_hand.write("---\n")
            wrap_hand.write("layout: docu\n")
            wrap_hand.write("---\n")
            old_name = dire + "/" + filename
            s1 = "{% include_relative " + old_name + "%}\n"
            wrap_hand.write(s1)
            wrap_hand.close()
