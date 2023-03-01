import os
import sys
from os import listdir
from os.path import isfile, join
import yaml
from yaml import load, FullLoader
import re


# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


def load_config():
    # First check in current dir and if not found in /etc
    try:
        stream = open("rexync_conf.yml", "r")
    except:
        try:
            stream = open("/etc/rexync.conf.yml", "r")
        except:
            print("Unable to open rexync_conf.yml")
            exit(-1)

    global yaml_conf
    global rules

    rules={}
    yaml_conf = load(stream, Loader=yaml.FullLoader)["rexync"]

    for rule in yaml_conf["rules"]:
        print(rule)
        pattern = rule["rule"]["pattern"]
        description = rule["rule"]["description"]
        capture_groups = rule["rule"]["capture_groups"]

        rules[pattern] = { "description": description, "capture_groups": capture_groups }

    print(yaml_conf)
    print(rules)

def match_name(f_name):
    for key in rules:
        res = re.search(key, f_name)
        if res:
            desc = rules[key]["description"]
            cgroups = rules[key]["capture_groups"]

            for g in res.groups():
                print(g)

            info = { n: v for (n, v) in zip(cgroups, [g for g in res.groups()])}
            print(info)

            return info

    return False

def copy_file(from_dir, file_name, metadata):
    dest_base_dir = yaml_conf["dest_base_dir"]
    link_src = os.path.join(from_dir, file_name)
    season = metadata["season"]
    dest_dir = os.path.join(dest_base_dir, metadata["title"], f"Season {season}")
    os.makedirs(dest_dir, exist_ok=True)
    dest_link = os.path.join(dest_dir, file_name)
    os.link(link_src, dest_link)

def process_dir(dir_name):
    onlyfiles = [f for f in listdir(dir_name) if isfile(join(dir_name, f))]

    for file in onlyfiles:
        res = match_name(file)
        if res:
            copy_file(dir_name, file, res)

    return onlyfiles

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    load_config()

    print(process_dir(sys.argv[1]))
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
