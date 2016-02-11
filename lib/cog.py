import json
import string
import os
import sys

def send_json(data):
    print "JSON\n"
    print "%s\n" % (json.dumps(data))
    sys.stdout.flush()

def send_error(text):
    send_json({"error": text})

def command_name():
    return os.getenv("COG_COMMAND")

def name_to_option_var(name):
    return "COG_OPT_" + string.upper(name)

def index_to_arg_var(index):
    return "COG_ARGV_" + str(index)

def has_option(name):
    var_name = name_to_option_var(name)
    return os.getenv(var_name) is not None

def get_option(name, default = None):
    var_name = name_to_option_var(name)
    var_value = os.getenv(var_name)
    if var_value is None:
        return default
    else:
        return var_value

def pretty_null(value):
    if value is None:
        return "n/a"
    else:
        return value

def get_arg_count():
    arg_count = os.getenv("COG_ARGC")
    if arg_count is None:
        return 0
    else:
        return int(arg_count)

def get_arg(index, default = None):
    arg_var = index_to_arg_var(index)
    return os.getenv(arg_var, default)

def collect_args():
    args = []
    for i in range(0, get_arg_count()):
        args.append(get_arg(i))
    return args
