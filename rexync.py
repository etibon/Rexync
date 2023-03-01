#!/usr/bin/python3
import os
import sys
from os import listdir
from os.path import isfile, join
import yaml
from yaml import load, FullLoader
import re
from glob import glob


def load_config():
    # First check in current dir and if not found in /etc
    conf_path="rexync_conf.yml"
    try:
        stream = open(conf_path, "r")
    except:
        try:
            conf_path="/etc/rexync_conf.yml"
            stream = open(conf_path, "r")
        except:
            print("Unable to open rexync_conf.yml")
            exit(-1)

    global yaml_conf
    global rules

    rules={}
    yaml_conf = load(stream, Loader=yaml.FullLoader)["rexync"]

    print(yaml_conf)

    for rule in yaml_conf["rules"]:
        pattern = rule["pattern"]
        description = rule["description"]
        capture_groups = rule["capture_groups"]
        category = rule["category"]

        rules[pattern] = { "description": description, "capture_groups": capture_groups, "category": category }

    print(f"Loaded {len(rules)} rules from {conf_path}")

def match_name(f_name):
    for key in rules:
        res = re.search(key, f_name)
        if res:
            desc = rules[key]["description"]
            cgroups = rules[key]["capture_groups"]
            rule_category = rules[key]["category"]

            if rule_category == category:
                info = { n: v for (n, v) in zip(cgroups, [g for g in res.groups()])}

                return info

    return False

def copy_file(from_dir, file_name, metadata):
    dest_base_dir = yaml_conf["dest_base_dir"]
    link_src = os.path.join(from_dir, file_name)
    if category=="shows":
        season = metadata["season"]
        dest_dir = os.path.join(dest_base_dir, category, metadata["title"], f"Season {season}")
    else:
        dest_dir = os.path.join(dest_base_dir, category)

    os.makedirs(dest_dir, exist_ok=True)
    dest_link = os.path.join(dest_dir, os.path.basename(file_name))

    if not os.path.exists(dest_link):
        os.link(link_src, dest_link)
        print(f"Created link from {link_src} to {dest_link}.")
    else:
        print(f"File already linked in destination {dest_link} - skipped.")


def process_dir(dir_name):
    print(f"Processing folder {dir_name} ...")
    onlyfiles = [os.path.relpath(y, dir_name) for x in os.walk(dir_name) for y in glob(os.path.join(x[0], '*'))]
    # onlyfiles = [f for f in listdir(dir_name) if isfile(join(dir_name, f))]

    processed_files=[]
    for file in onlyfiles:
        res = match_name(os.path.basename(file))
        if res:
            print(f"Identified match for file {file}...")
            copy_file(dir_name, file, res)
            processed_files.append(file)

    return processed_files

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    load_config()

    if len(sys.argv) < 3:
        print("Please provide an input directory and a category")
        exit(-1)
    global category
    category = sys.argv[2]

    process_dir(sys.argv[1])
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
