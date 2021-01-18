from config import Config
import getopt, sys, csv,  argparse 

def usage():
    print('help')

def generate_child(mq, shortcut, prop, val, slc=""):
    for i in range(1, Config.child_limit+1, 1):
        uprop = "{ %s }" % get_property(mq, prop, Config.templates["childcalc"].format(n=i))
        css = Config.templates["child"].format(mq=mq, cls=shortcut, n=i, prop=uprop, slc=slc)    
        print(css)

def generate_length(mq, shortcut, prop, val, slc=""):
    for u in Config.unit:
        m = u.split("|")
        name = m[0]
        unit = m[1] if len(m) > 1 else m[0]
        for r in Config.unit[u]:
            for i in range(r[0], r[1]+r[2], r[2]):
                val = "{nbr}{unit}".format(nbr=i, unit=unit)
                uprop = "{ %s }" % get_property(mq, prop, val)
                val = "{name}{nbr}".format(name=name, nbr=i)
                css = Config.templates["default"].format(mq=mq, cls=shortcut, val=val, prop=uprop, slc=slc)
                print(css)

def generate_onefourlength(mq, shortcut, prop, val, slc=""):
    for u in Config.unit:
        m = u.split("|")
        name = m[0]
        unit = m[1] if len(m) > 1 else m[0]
        for r in Config.unit[u]:
            for i in range(r[0], r[1]+r[2], r[2]):
                val = "{nbr}{unit}".format(nbr=i, unit=unit)
                uprop = "{ %s }" % get_property(mq, prop, val)
                val = "{name}{nbr}".format(name=name, nbr=i)
                css = Config.templates["default"].format(mq=mq, cls=shortcut, val=val, prop=uprop, slc=slc)
                print(css)

def generate_topbot(mq, shortcut, prop, val, slc=""):
    shortcut = "%sy" % shortcut
    for u in Config.unit:
        m = u.split("|")
        name = m[0]
        unit = m[1] if len(m) > 1 else m[0]
        for r in Config.unit[u]:
            for i in range(r[0], r[1]+r[2], r[2]):
                val = "{nbr}{unit}".format(nbr=i, unit=unit)
                uprop = "{ %s }" % get_topbot(mq, prop, val)
                val = "{name}{nbr}".format(name=name, nbr=i)
                css = Config.templates["default"].format(mq=mq, cls=shortcut, val=val, prop=uprop, slc="")
                print(css)

def generate_leftright(mq, shortcut, prop, val, slc=""):
    shortcut = "%sx" % shortcut
    for u in Config.unit:
        m = u.split("|")
        name = m[0]
        unit = m[1] if len(m) > 1 else m[0]
        for r in Config.unit[u]:
            for i in range(r[0], r[1]+r[2], r[2]):
                val = "{nbr}{unit}".format(nbr=i, unit=unit)
                uprop = "{ %s }" % get_leftright(mq, prop, val)
                val = "{name}{nbr}".format(name=name, nbr=i)
                css = Config.templates["default"].format(mq=mq, cls=shortcut, val=val, prop=uprop, slc="")
                print(css)

def get_onefourlength(mq, prop, val, slc=""):
    if prop in Config.exceptions and val in Config.exceptions[prop]:
        return Config.templates["onefourlength"].format(mq=mq, prop=prop, val=Config.exceptions[prop][val], slc=slc)
    return Config.templates["onefourlength"].format(mq=mq, prop=prop, val=val, slc=slc)

def get_topbot(mq, prop, val, slc=""):
    if prop in Config.exceptions and val in Config.exceptions[prop]:
        return Config.templates["topbot"].format(mq=mq, prop=prop, val=Config.exceptions[prop][val], slc=slc)
    return Config.templates["topbot"].format(mq=mq, prop=prop, val=val, slc=slc)
        
def get_leftright(mq, prop, val, slc=""):
    if prop in Config.exceptions and val in Config.exceptions[prop]:
        return Config.templates["leftright"].format(mq=mq, prop=prop, val=Config.exceptions[prop][val], slc=slc)
    return Config.templates["leftright"].format(mq=mq, prop=prop, val=val, slc=slc)

def get_property(mq, prop, val, slc=""):
    if prop in Config.exceptions and val in Config.exceptions[prop]:
        return Config.templates["property"].format(mq=mq, prop=prop, val=Config.exceptions[prop][val], slc=slc)
    return Config.templates["property"].format(mq=mq, prop=prop, val=val, slc=slc)

def generate_css(mq, shortcut, prop, val):
    if hasattr(sys.modules[__name__], "generate_%s" % val):
        getattr(sys.modules[__name__], "generate_%s" % val)(mq, shortcut, prop, val, "")
    else:
        uprop = "{ %s }" % get_property(mq, prop, val)
        css = Config.templates["default"].format(mq=mq, cls=shortcut, val=val, prop=uprop, slc="")
        print(css)
    if prop in Config.hover:
        if hasattr(sys.modules[__name__], "generate_%s" % val):
            getattr(sys.modules[__name__], "generate_%s" % val)(mq, shortcut, prop, val, "-hv:hover")
        else:
            uprop = "{ %s }" % get_property(mq, prop, val)
            css = Config.templates["default"].format(mq=mq, cls=shortcut, val=val, prop=uprop, slc="-hv:hover")
            print(css)

def load_csv(mq):
    with open(filecsv) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=Config.csv["delimiter"])
        for row in reader:
            for value in row["values"].split(Config.csv["valuesdelimiter"]):
                generate_css(mq, row["shortcut"], row["property"], value)

def start():
    if default:
        print("/* Init default */")
        for d in Config.default: print(d)
    if widgets:
        print("/* Widgets */")
        for w in Config.widget: print(w % ".")
    if filters:
        print("/* Filters */")
        for f in Config.filters: print(f)
    if mediaqueries:
        print("/* Media Queries base */")
        load_csv(".")
        for mq in mediaqueries:
            mq = mq.split(',')
            print("/* Media Queries %s */" % mq[0])
            print("@media (max-width: %spx) {" % mq[1])    
            for w in Config.widget: print(w % ".%s-" % mq[0])
            load_csv(".%s-" % mq[0])
            print("}")
        for mq in mediaqueries:
            mq = mq.split(',')
            print("\n/* Media Queries %s */" % mq[0])
            print("@media (min-width: %spx) {" % mq[1])    
            for w in Config.widget: print(w % ".o%s-" % mq[0])
            load_csv(".o%s-" % mq[0])
            print("}")

def main():
    global mediaqueries, filecsv, default, widgets, filters
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--mediaqueries', help='Media queries', nargs='+')
    parser.add_argument('-c', '--csv', help='CSV', required=True)
    parser.add_argument('-d', '--default', help='CSV', action="store_true")
    parser.add_argument('-w', '--widgets', help='CSV', action="store_true")
    parser.add_argument('-f', '--filters', help='CSV', action="store_true")
    args = parser.parse_args()
    mediaqueries = args.mediaqueries
    default = args.default
    widgets = args.widgets
    filters = args.filters
    filecsv = args.csv
    start()

if __name__ == "__main__":
    main()