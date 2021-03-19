import argparse, datetime, getpass, json, os, lxml.html, pycurl, sys
from pathlib import Path
from io import BytesIO

CSS3_URL = "https://www.w3schools.com/cssref/"
BASE_DIR = Path(__file__).resolve(strict=True).parent
DEFAULT_CONFIG = "%s/config.json" % BASE_DIR
DEFAULT_CSS = "%s/wr.css" % BASE_DIR
HEADERS = {}
CSS3_JSON = "%s/css3.json" % BASE_DIR
VALUES_TABLES = {
    "property_values": "Property Values",
    "filter_functions": "Filter Functions",
    "media_types": "Media Types",
    "media_features": "Media Features",
}
CLASSUSED = []
CLASSCONFIG = {}
PROPUSED = []
PROPCONFIG = {}

class Template:
    default = ".{mq}{cls}-{val}{slc}, .{mq}{cls}-{val}-ch{slc} > *, .{mq}{cls}-{val}-rs{slc} * {prop}"
    child = ".{mq}{cls}-ch > *:first-child:nth-last-child({n}), .{mq}{cls}-ch > *:first-child:nth-last-child({n}) ~ * {prop}"
    calc =  "calc(100%% / %s)"
    prop = "{ %s: %s; }"
    doubleprop = "{ %s: %s; %s: %s; }"

class Split:
    syntax = ":"
    values = "|"

class user:
    id = None
    username = None

class Log:
    logger = "logger_{}"
    log_type = "console"
    log_level = "debug"
    format_syslog = "[{}] {}"
    format_file = "{}:{}:{}.{} - {} | [{}] {}\n"
    format_console = "{}{}:{}:{}.{} - {} | [{}] {}{}"
    format_user = "{}.{} - {}"
    format_lvl = "{}_lvl"
    format_color = "{}_color"
    file_open_method = "a"
    name_file = "{}/{}_{}_{}_{}.log"
    default_color = "\033[0m"
    emerg_lvl = 0
    emerg_color = "\033[1;93;5;101m"
    alert_lvl = 1
    alert_color = "\033[1;30;5;105m"
    crit_lvl = 2
    crit_color = "\033[1;97;5;101m"
    error_lvl = 3
    error_color = "\033[1;91;5;107m"
    warning_lvl = 4
    warning_color = "\033[0;91m"
    notice_lvl = 5
    notice_color = "\033[0;97m"
    info_lvl = 6
    info_color = "\033[0;94m"
    debug_lvl = 7
    debug_color = "\033[0;30;100m"

def logger(app, lvl, msg, user=None):
    code = lvl
    lvl = getattr(Log, Log.format_lvl.format(lvl))
    aut = getattr(Log, Log.format_lvl.format(Log.log_level))
    if lvl <= aut:
        if user is not None:
            msg = Log.format_user.format(user.username, user.id, msg)
        if Log.log_type == "syslog":
            logger_syslog(app, lvl, code, msg)
        elif Log.log_type == "file":
            logger_file(app, lvl, code, msg)
        else:
            logger_console(app, lvl, code, msg)

# Logger in syslog
def logger_syslog(app, lvl, code, msg):
    syslog.openlog(logoption=syslog.LOG_PID)
    syslog.syslog(code, Log.format_syslog.format(app, msg))
    syslog.closelog()

# Logger in file
def logger_file(app, lvl, code, msg):
    now = datetime.datetime.now()
    logfile = Log.name_file.format(conf.Directory.logs, app, now.year, now.month, now.day)
    log = open(logfile, Log.file_open_method)
    log.write(Log.format_file.format(now.hour, now.minute, now.second, now.microsecond, lvl, app, msg))
    log.close()

# Logger in console
def logger_console(app, lvl, code, msg):
    color = getattr(Log, Log.format_color.format(code))
    now = datetime.datetime.now()
    print(Log.format_console.format(color, now.hour, now.minute, now.second, now.microsecond, lvl, app, msg, Log.default_color))

def header_function(header_line):
    header_line = header_line.decode("iso-8859-1")
    if ":" not in header_line: return
    name, value = header_line.split(":", 1)
    name = name.strip()
    value = value.strip()
    name = name.lower()
    HEADERS[name] = value

def getpage(location):
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, location)
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.HEADERFUNCTION, header_function)
    c.setopt(c.FOLLOWLOCATION, 1)
    c.perform()
    c.close()
    body = buffer.getvalue().decode("utf-8")
    return lxml.html.document_fromstring(body)

def prepare():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--colors", help="Enable colors, default: False", action="store_true", default=False)
    parser.add_argument("-d", "--debug", help="Debug level, default: %s" % Log.log_level, default=Log.log_level)
    parser.add_argument("-f", "--filters", help="Enable filters, default: False", action="store_true", default=False)
    parser.add_argument("-l", "--log", help="Enable widgets, default: %s" % Log.log_type, default=Log.log_type)
    parser.add_argument("-o", "--output", help="Output css, default: %s" % DEFAULT_CSS, default=DEFAULT_CSS)
    parser.add_argument("-r", "--reverse", help="Reverse media queries, default: False", action="store_true", default=False)
    parser.add_argument("-s", "--setting", help="Specify the file config, default: %s" % DEFAULT_CONFIG, default=DEFAULT_CONFIG)
    parser.add_argument("-v", "--verbose", help="Enable widgets, default: False", action="store_true", default=False)
    parser.add_argument("-w", "--widgets", help="Enable widgets, default: False", action="store_true", default=False)
    args = parser.parse_args()
    
    global CONFIG_FILE, CSS_FILE, DEBUG, FILTERS, REVERSE, VERBOSE, WIDGETS, COLORS
    CONFIG_FILE = args.setting
    Log.log_level = args.debug
    FILTERS = args.filters
    COLORS = args.colors
    Log.log_type = args.log
    CSS_FILE = args.output
    REVERSE = args.reverse
    print(REVERSE)
    VERBOSE = args.verbose
    WIDGETS = args.widgets

def getsyntax(properties, body):
    text = "Syntax"
    nxt = False
    for tag in body:
        if nxt:
            return tag.text_content().strip().replace('%', 'percent').replace("[", "").replace("]", "")
            break
        nxt = True if tag.tag == "h2" and text in tag.text_content() else False
            
def getvalues(properties, body, text):
    nxt = False
    for tag in body:
        if nxt and tag.tag == "div":
            values = []
            for tr in tag.xpath(".//table")[0]:
                if tr[0].tag == 'td':
                    toadds = tr[0].text_content().strip().replace('%', 'percent').replace("[", "").replace("]", "")
                    if "matrix3d" in toadds:
                        values += ["".join([toadd.strip() for toadd in toadds.splitlines()])]
                    else:
                        values += [toadd.strip() for toadd in toadds.splitlines()]
            return values
            break
        nxt = True if tag.tag == "h2" and tag.text_content() == text else False
    return None

def getproperties(body):
    for alphtable in body.xpath('//div[@id="cssproperties"]/table'):
        for tr in alphtable:
            if tr[0].xpath(".//a"):
                prop = tr[0].text_content().strip()
                logger("wreasy", "debug", "property: %s" % prop, user)
                href = CSS3_URL + tr[0][0].attrib["href"].strip().replace("/cssref", "")
                logger("wreasy", "debug", "href: %s" % href, user)
                CSS3_PROPERTIES[prop] = {"href": href}
                bodyproperty = getpage(href).xpath('//*[@id="main"]')[0]
                syntax = getsyntax(prop, bodyproperty).replace('\r\n', '')
                if syntax: CSS3_PROPERTIES[prop]["syntax"] = syntax
                for key,text in VALUES_TABLES.items():
                    values = getvalues(prop, bodyproperty, text)
                    if values: CSS3_PROPERTIES[prop][key] = values

def getmelted_default(prop, value, *args, **kwargs):
    propname = value if kwargs.get("propname", False) else getprop(value)
    template = {
        "mq": kwargs.get("mq", ""),
        "cls": getclass(prop),
        "val": propname,
        "slc": kwargs.get("slc", ""),
        "prop": Template.prop % (prop, value)
    }
    print(Template.default.format(**template))

def getmelted_percentage(prop, value, *args, **kwargs):
    getmelted_percent(prop, value, *args, **kwargs)

def getmelted_percent(prop, value, *args, **kwargs):
    if "length" not in CSS3_PROPERTIES[prop]["property_values"]:
        name = CONFIG["percent"].split(Split.values)[0]
        unity = CONFIG["percent"].split(Split.values).pop()
        for v in CONFIG["length"][CONFIG["percent"]]:
            for i in range(v[0], v[1]+v[2], v[2]):
                val = "{nbr}{unit}".format(nbr=i, unit=unity)
                template = {
                    "mq": kwargs.get("mq", ""),
                    "cls": getclass(prop),
                    "val": name+str(i),
                    "slc": kwargs.get("slc", ""),
                    "prop": Template.prop % (prop, val)
                }
                print(Template.default.format(**template))

def getmelted_length(prop, value, *args, **kwargs):
    unities = CONFIG[prop] if prop in CONFIG else CONFIG["length"]
    for key, values in unities.items():
        name = key.split(Split.values)[0]
        unity = key.split(Split.values).pop()
        for v in values:
            for i in range(v[0], v[1]+v[2], v[2]):
                val = "{nbr}{unit}".format(nbr=i, unit=unity)
                template = {
                    "mq": kwargs.get("mq", ""),
                    "cls": getclass(prop),
                    "val": name+str(i),
                    "slc": kwargs.get("slc", ""),
                    "prop": Template.prop % (prop, val)
                }
                print(Template.default.format(**template))

def getmelted_inherit(prop, value, *args, **kwargs):
    pass

def getmelted_initial(prop, value, *args, **kwargs):
    pass

def getmelted_value(prop, value, *args, **kwargs):
    getmelted_length(prop, value, *args, **kwargs)

def getmelted_lrtb(prop, value, axis, *args, **kwargs):
    unities = CONFIG[prop] if prop in CONFIG else CONFIG["length"]
    lrtb = "leftright" if axis == "x" else "topbot"
    for key, values in unities.items():
        name = key.split(Split.values)[0]
        unity = key.split(Split.values).pop()
        for v in values:
            for i in range(v[0], v[1]+v[2], v[2]):
                val = "{nbr}{unit}".format(nbr=i, unit=unity)
                template = {
                    "mq": kwargs.get("mq", ""),
                    "cls": getclass(prop),
                    "val": name+str(i)+axis,
                    "slc": kwargs.get("slc", ""),
                    "prop": Template.doubleprop % (CONFIG[lrtb][prop][0], val, CONFIG[lrtb][prop][1], val)
                }
                print(Template.default.format(**template))

def getmelted_number(prop, value, *args, **kwargs):
    unities = CONFIG[prop] if prop in CONFIG else CONFIG["length"]
    fm = 1 if prop == "opacity" else 1
    by = 1 if prop == "opacity" else 1
    to = 10 if prop == "opacity" else CONFIG["number"]
    for i in range(fm, to+by, by):
        template = {
            "mq": kwargs.get("mq", ""),
            "cls": getclass(prop),
            "val": str(i),
            "slc": kwargs.get("slc", ""),
            "prop": Template.prop % (prop, i/10 if prop == "opacity" else i)
        }
        print(Template.default.format(**template))


def getmelted_child(prop, value, *args, **kwargs):
    unities = CONFIG[prop] if prop in CONFIG else CONFIG["length"]
    for i in range(1, CONFIG["childlimit"]+1, 1):
        val = Template.calc % i
        template = {
            "mq": kwargs.get("mq", ""),
            "cls": getclass(prop),
            "val": "test",
            "slc": kwargs.get("slc", ""),
            "prop": Template.prop % (prop, val),
            "n": i,
        }
        print(Template.child.format(**template))

def getmeltedproperty(prop, value, *args, **kwargs):
    if value not in CONFIG["ignored"]:
        if hasattr(sys.modules[__name__], "getmelted_%s" % value):
            getattr(sys.modules[__name__], "getmelted_%s" % value)(prop, value, *args, **kwargs)
        else:
            getattr(sys.modules[__name__], "getmelted_default")(prop, value, *args, **kwargs)

def getallcss():
    if REVERSE:
        print("/* Media Queries base */")
        getcss()
        for w in CONFIG["widgets"]: 
            print(w % {"mq": "."})
        for mq, value in CONFIG["media-queries"].items():
            print("/* Media Queries %s */" % mq)
            print("@media (max-width: %spx) {" % value)
            getcss(mq+"-")
            for w in CONFIG["widgets"]: 
                print(w % {"mq": ".%s-" % mq})
            print("}")
    else:
        print("/* Media Queries base */")
        getcss()
        for w in CONFIG["widgets"]: 
            print(w % {"mq": "."})
        for mq, value in CONFIG["media-queries"].items():
            print("/* Media Queries %s */" % mq)
            print("@media (min-width: %spx) {" % value)
            getcss(mq+"-")
            for w in CONFIG["widgets"]: 
                print(w % {"mq": ".%s-" % mq})
            print("}")
    

def getcss(mq=""):
    for prop, config in CSS3_PROPERTIES.items():
        if "@" not in prop and "syntax" in config and prop not in CONFIG["ignored"]:
            if CONFIG["used"] == "*" or prop in CONFIG["used"]:
                pty, syn = [syntax.strip() for syntax in config["syntax"][0:-1].split(Split.syntax)]
                args = syn.split()
                if len(args) == 1:
                    values = args.pop()
                    clas = getclass(prop)
                    for value in config['property_values']:
                        getmeltedproperty(prop, value, **{"mq": mq})
                if prop in CONFIG["leftright"]:
                    getmelted_lrtb(prop, value, "x", *args, **{"mq": mq})
                if prop in CONFIG["topbot"]:
                    getmelted_lrtb(prop, value, "y", *args, **{"mq": mq})
                if prop in CONFIG["child"]:
                    getmelted_child(prop, value, *args, **{"mq": mq})
    if COLORS:
        for color in CONFIG["colors"]:
            getmelted_default("background-color", color, **{"mq": mq, "propname": True})
            getmelted_default("color", color, **{"mq": mq, "propname": True})


def getprop(prop):
    clasok = True
    i = 0
    if prop in PROPCONFIG:
        return PROPCONFIG[prop]
    while clasok:
        i+=1
        clas = "".join([pt[0:i] for pt in prop.split('-')])
        if clas not in PROPUSED:
            PROPUSED.append(clas)
            PROPCONFIG[prop] = clas
            return clas
            clasok = False
    return clas

def getclass(prop):
    clasok = True
    i = 0
    if prop in CLASSCONFIG:
        return CLASSCONFIG[prop]
    while clasok:
        i+=1
        clas = "".join([pt[0:i] for pt in prop.split('-')])
        if clas not in CLASSUSED:
            CLASSUSED.append(clas)
            CLASSCONFIG[prop] = clas
            return clas
            clasok = False
    return clas

def main():
    global CSS3_PROPERTIES, CONFIG
    CSS3_PROPERTIES = {}

    prepare()
    with open(CONFIG_FILE) as json_file:
        CONFIG = json.load(json_file)
    logger("wreasy", "debug", "start", user)

    if not os.path.isfile(CSS3_JSON):
        getproperties(getpage(CSS3_URL))
        logger("wreasy", "debug", "properties create: %s" % len(CSS3_PROPERTIES), user)
        with open(CSS3_JSON, "w") as outfile:
            json.dump(CSS3_PROPERTIES, outfile, indent=4)

    with open(CSS3_JSON) as json_file:
        CSS3_PROPERTIES = json.load(json_file)
    getallcss()
    logger("wreasy", "debug", "stop", user)

if __name__ == "__main__":
    user.username = getpass.getuser()
    user.id = os.getegid()
    main()