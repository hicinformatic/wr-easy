class Config:
    default = [
        "html, body { margin: 0 auto;}",
        "* { box-sizing: border-box; margin: 0; padding: 0 }",
    ]

    widget = [
        """input[type="checkbox"]%sdsc:not(:checked) ~ * { display: none; }""",
        """input[type="radio"]%sdsc:not(:checked) ~ * { display: none; }""",
    ]

    filters = [
        ".sh-pr10 { background-color: rgba(0, 0, 0, 0.1); }"
        ".sh-pr15 { background-color: rgba(0, 0, 0, 0.15); }"
        ".sh-pr20 { background-color: rgba(0, 0, 0, 0.2); }"
        ".sh-pr25 { background-color: rgba(0, 0, 0, 0.25); }"
        ".sh-pr50 { background-color: rgba(0, 0, 0, 0.5); }"
        ".sh-pr100 { background-color: rgba(0, 0, 0, 1); }"
        ".fil-blur-px5 { filter: blur(5px); }",
        ".fil-blur-px10 { filter: blur(10px); }",
        ".fil-grayscale-pr50 { filter: grayscale(50%); }",
        ".fil-grayscale-pr100 { filter: grayscale(100%); }",
        ".fil-opacity-50 { filter: opacity(50%); }",
        ".fil-opacity-pr100 { filter: opacity(100%); }",
        ".fil-sepia-pr50 { filter: sepia(50%); }",
        ".fil-sepia-pr100 { filter: sepia(100%); }",
    ]

    unit = {
        "px": [[0, 20, 1], [25, 100, 5], [150, 1000, 50]],
        #"em": [[0, 10, 1], [20, 100, 5], [100, 500, 50]],
        "pr|%": [[0, 20, 1], [25, 100, 5]],
    }

    child_limit = 20

    exceptions = {
        "margin": { "auto": "0 auto"},
        "padding": { "auto": "0 auto"},
    }

    hover = ["color", "background-color"]

    templates = {
        "default": "{mq}{cls}-{val}{slc}, {mq}{cls}-{val}-ch{slc} > *, {mq}{cls}-{val}-rs{slc} * {prop}",
        "child": "{mq}{cls}-ch > *:first-child:nth-last-child({n}), {mq}{cls}-ch > *:first-child:nth-last-child({n}) ~ * {prop}",
        "childcalc": "calc(100%/{n})",
        "property": "{prop}: {val};",
        "onefourlength": "{prop}: {val} {val} {val} {val}",
        "length": "{lgt}{unit}",
        "topbot": "{prop}-top: {val}; {prop}-bottom: {val};",
        "leftright": "{prop}-left: {val}; {prop}-right: {val};",
    }
    
    csv = { "base": "csv/colors.csv", "delimiter": ",", "valuesdelimiter": "|", }
    media_queries = { "lg": 1200, "md": 992, "sm": 768, }