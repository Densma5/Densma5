import os
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


# =========================================================
# CONFIG
# =========================================================

USERNAME = os.environ.get("GITHUB_USERNAME", "Densma5")
TOKEN = os.environ["GH_TOKEN"]

START_YEAR = 2023
CURRENT_YEAR = datetime.now(timezone.utc).year
YEARS = list(range(START_YEAR, CURRENT_YEAR + 1))


# Colors
BACKGROUND = "#0D1117"
CARD_BACKGROUND = "#11161D"

PURPLE = "#9900FF"
PURPLE_LIGHT = "#B833FF"
PURPLE_DARK = "#540080"

TEXT = "#F0F6FC"
MUTED = "#8B949E"
DIVIDER = "#30363D"


# =========================================================
# GITHUB GRAPHQL
# =========================================================

QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        totalContributions
      }
    }
  }
}
"""


def get_contributions(year):

    variables = {
        "login": USERNAME,
        "from": f"{year}-01-01T00:00:00Z",
        "to": f"{year}-12-31T23:59:59Z",
    }

    payload = json.dumps({
        "query": QUERY,
        "variables": variables
    }).encode("utf-8")

    request = urllib.request.Request(
        "https://api.github.com/graphql",
        data=payload,
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": "github-profile-contribution-stats"
        }
    )

    with urllib.request.urlopen(request) as response:
        result = json.loads(response.read())

    if "errors" in result:
        raise RuntimeError(result["errors"])

    user = result["data"]["user"]

    if user is None:
        raise RuntimeError(
            f"GitHub user '{USERNAME}' was not found."
        )

    return (
        user["contributionsCollection"]
        ["contributionCalendar"]
        ["totalContributions"]
    )


# =========================================================
# GET DATA
# =========================================================

year_data = {}

for year in YEARS:
    print(f"Getting contributions for {year}...")
    year_data[year] = get_contributions(year)


total_contributions = sum(year_data.values())

current_year_contributions = year_data.get(
    CURRENT_YEAR,
    0
)

best_year = max(
    year_data,
    key=year_data.get
)

best_year_contributions = year_data[best_year]

active_years = sum(
    1
    for contributions in year_data.values()
    if contributions > 0
)

max_year_value = max(
    year_data.values(),
    default=1
)


# =========================================================
# SVG
# =========================================================

WIDTH = 1400
HEIGHT = 430

svg = []


svg.append(
    f"""
<svg
    xmlns="http://www.w3.org/2000/svg"
    width="{WIDTH}"
    height="{HEIGHT}"
    viewBox="0 0 {WIDTH} {HEIGHT}">
"""
)


# =========================================================
# STYLES
# =========================================================

svg.append(
    f"""
<style>

text {{
    font-family:
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        Helvetica,
        Arial,
        sans-serif;
}}

.title {{
    fill: {TEXT};
    font-size: 38px;
    font-weight: 700;
}}

.subtitle {{
    fill: {MUTED};
    font-size: 13px;
    letter-spacing: 5px;
}}

.main-number {{
    fill: {TEXT};
    font-size: 38px;
    font-weight: 700;
}}

.purple-number {{
    fill: {PURPLE_LIGHT};
    font-size: 38px;
    font-weight: 700;
}}

.stat-label {{
    fill: {MUTED};
    font-size: 12px;
    letter-spacing: 1px;
}}

.year {{
    fill: {TEXT};
    font-size: 16px;
    font-weight: 600;
}}

.year-number {{
    fill: {PURPLE_LIGHT};
    font-size: 25px;
    font-weight: 700;
}}

.year-label {{
    fill: {MUTED};
    font-size: 12px;
}}

.footer {{
    fill: {MUTED};
    font-size: 12px;
    letter-spacing: 4px;
}}

</style>
"""
)


# =========================================================
# BACKGROUND
# =========================================================

svg.append(
    f"""
<defs>
    <linearGradient
        id="purpleGradient"
        x1="0%"
        y1="0%"
        x2="100%"
        y2="0%"
    >
        <stop
            offset="0%"
            stop-color="{PURPLE_DARK}"
        />
        <stop
            offset="100%"
            stop-color="{PURPLE}"
        />
    </linearGradient>
</defs>
"""
)


svg.append(
    f"""
<rect
    x="1"
    y="1"
    width="{WIDTH - 2}"
    height="{HEIGHT - 2}"
    rx="22"
    fill="{BACKGROUND}"
    stroke="{PURPLE}"
    stroke-width="2"
/>
"""
)


# =========================================================
# HEADER
# =========================================================

svg.append(
    f"""
<text
    x="55"
    y="67"
    class="title"
>
    GitHub
    <tspan fill="{PURPLE}">
        Contributions
    </tspan>
</text>
"""
)




# =========================================================
# MAIN STATS
# =========================================================

main_stats = [
    (
        f"{total_contributions:,}",
        "TOTAL CONTRIBUTIONS"
    ),
    (
        f"{current_year_contributions:,}",
        f"{CURRENT_YEAR} CONTRIBUTIONS"
    ),
    (
        str(best_year),
        "BEST YEAR"
    ),
    (
        str(active_years),
        "ACTIVE YEARS"
    ),
]


stats_start_x = 560
stat_width = 195


for index, (number, label) in enumerate(main_stats):

    x = stats_start_x + (index * stat_width)

    if index > 0:

        svg.append(
            f"""
<line
    x1="{x - 28}"
    y1="35"
    x2="{x - 28}"
    y2="120"
    stroke="{DIVIDER}"
/>
"""
        )

    css_class = (
        "main-number"
        if index == 0
        else "purple-number"
    )

    svg.append(
        f"""
<text
    x="{x}"
    y="67"
    class="{css_class}"
>
    {number}
</text>
"""
    )

    svg.append(
        f"""
<text
    x="{x}"
    y="96"
    class="stat-label"
>
    {label}
</text>
"""
    )


# =========================================================
# DIVIDER
# =========================================================

svg.append(
    f"""
<line
    x1="55"
    y1="150"
    x2="{WIDTH - 55}"
    y2="150"
    stroke="{DIVIDER}"
/>
"""
)


# =========================================================
# YEAR CARDS
# =========================================================

available_width = WIDTH - 110

year_width = (
    available_width
    / len(YEARS)
)


for index, year in enumerate(YEARS):

    x = 55 + (
        index * year_width
    )

    center = (
        x
        + year_width / 2
    )

    contributions = (
        year_data[year]
    )

    bar_max_width = (
        year_width - 55
    )

    if max_year_value > 0:

        bar_width = (
            contributions
            / max_year_value
        ) * bar_max_width

    else:

        bar_width = 0


    # Year

    svg.append(
        f"""
<text
    x="{center}"
    y="205"
    text-anchor="middle"
    class="year"
>
    {year}
</text>
"""
    )


    # Contribution number

    svg.append(
        f"""
<text
    x="{center}"
    y="248"
    text-anchor="middle"
    class="year-number"
>
    {contributions:,}
</text>
"""
    )


    svg.append(
        f"""
<text
    x="{center}"
    y="275"
    text-anchor="middle"
    class="year-label"
>
    contributions
</text>
"""
    )


    # Bar background

    bar_x = (
        center
        - bar_max_width / 2
    )

    svg.append(
        f"""
<rect
    x="{bar_x}"
    y="302"
    width="{bar_max_width}"
    height="7"
    rx="4"
    fill="{DIVIDER}"
/>
"""
    )


    # Purple activity bar

    svg.append(
        f"""
<rect
    x="{bar_x}"
    y="302"
    width="{bar_width}"
    height="7"
    rx="4"
    fill="url(#purpleGradient)"
/>
"""
    )


    # Separator

    if index < len(YEARS) - 1:

        separator_x = (
            x + year_width
        )

        svg.append(
            f"""
<line
    x1="{separator_x}"
    y1="185"
    x2="{separator_x}"
    y2="320"
    stroke="{DIVIDER}"
/>
"""
        )


# =========================================================
# FOOTER
# =========================================================

footer_y = 375

svg.append(
    f"""
<text
    x="{WIDTH - 410}"
    y="{footer_y + 5}"
    class="footer"
>
  
</text>
"""
)


svg.append("</svg>")


# =========================================================
# SAVE
# =========================================================

output = Path(
    "assets/contributions.svg"
)

output.parent.mkdir(
    parents=True,
    exist_ok=True
)

output.write_text(
    "\n".join(svg),
    encoding="utf-8"
)


# =========================================================
# LOG
# =========================================================

print()
print("Contribution stats generated successfully.")
print()

print(
    f"Total: "
    f"{total_contributions:,}"
)

print(
    f"Current year: "
    f"{current_year_contributions:,}"
)

print(
    f"Best year: "
    f"{best_year} "
    f"({best_year_contributions:,})"
)

print()

for year, count in year_data.items():

    print(
        f"{year}: "
        f"{count:,}"
    )
