#!/usr/bin/env python3
"""Static site generator for jackwetherell.github.io.

Pure standard library: no packages, no toolchain. Reads the page shell from
templates/base.html and the body of each page from content/<slug>.html, then
writes the finished pages to the repository root where GitHub Pages serves them.

    python3 build.py            # build every page
    python3 build.py --check    # fail if the committed pages are out of date
"""

import argparse
import datetime as _datetime
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent
SITE_URL = "https://jackwetherell.github.io"
AUTHOR = "Jack Wetherell"
OG_IMAGE = "images/outguess.jpg"

# Every page of the site. `nav` is the label used in the primary navigation;
# a page with nav=None is reachable but not listed (e.g. the 404 page).
PAGES = [
    {
        "slug": "index",
        "nav": None,
        "title": "Dr. Jack Wetherell — Research and Development Scientist",
        "description": (
            "Dr. Jack Wetherell is a research and development scientist working in "
            "imagineering, autonomous vehicles and quantum technologies, specialising "
            "in machine learning, computer vision, simulation and robotics."
        ),
    },
    {
        "slug": "profile",
        "nav": "Profile",
        "title": "Profile — Dr. Jack Wetherell",
        "description": (
            "Profile and contact details for Dr. Jack Wetherell, Lead R&D Imagineer at "
            "Walt Disney Imagineering and lead developer of the iDEA code."
        ),
    },
    {
        "slug": "research",
        "nav": "Research",
        "title": "Research and Development — Dr. Jack Wetherell",
        "description": (
            "Research and development in imagineering, autonomous vehicles and quantum "
            "technologies: robotics, simulation, machine learning, many-body "
            "perturbation theory and density functional theory."
        ),
    },
    {
        "slug": "idea",
        "nav": "iDEA",
        "title": "The iDEA Code — Dr. Jack Wetherell",
        "description": (
            "iDEA, the interacting Dynamic Electrons Approach: a free software framework "
            "in Python for research, testing and education in many-body quantum physics."
        ),
    },
    {
        "slug": "publications",
        "nav": "Publications",
        "title": "Publications — Dr. Jack Wetherell",
        "description": (
            "Peer-reviewed publications by Jack Wetherell in Physical Review B, Physical "
            "Review A, Physical Review Materials, Faraday Discussions and IEEE."
        ),
    },
    {
        "slug": "patents",
        "nav": "Patents",
        "title": "Patents — Dr. Jack Wetherell",
        "description": (
            "Granted and filed patents by Jack Wetherell covering modular omnidirectional "
            "actuated floors, projection technologies and simulation methods."
        ),
    },
    {
        "slug": "conf",
        "nav": "Conferences",
        "title": "Conferences and Talks — Dr. Jack Wetherell",
        "description": (
            "Conference organisation, invited talks and presentations given by "
            "Jack Wetherell."
        ),
    },
    {
        "slug": "colab",
        "nav": "Collaborators",
        "title": "Collaborators — Dr. Jack Wetherell",
        "description": (
            "Research collaborators of Jack Wetherell at Walt Disney Imagineering, "
            "École Polytechnique, the Max Planck Institute and the University of York."
        ),
    },
    {
        "slug": "teaching",
        "nav": "Teaching",
        "title": "Teaching and Supervision — Dr. Jack Wetherell",
        "description": (
            "Undergraduate teaching, tutoring, supervision and co-supervision by "
            "Jack Wetherell."
        ),
    },
    {
        "slug": "404",
        "nav": None,
        "title": "Page not found — Dr. Jack Wetherell",
        "description": "The page you were looking for could not be found.",
        "noindex": True,
        "absolute_urls": True,
    },
]

JSON_LD = """<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Person",
  "name": "Jack Wetherell",
  "givenName": "Jack",
  "familyName": "Wetherell",
  "honorificPrefix": "Dr.",
  "jobTitle": "Research and Development Scientist",
  "email": "mailto:jack.wetherell@gmail.com",
  "url": "%(site)s/",
  "image": "%(site)s/%(image)s",
  "address": {"@type": "PostalAddress", "addressLocality": "Los Angeles", "addressCountry": "USA"},
  "worksFor": {"@type": "Organization", "name": "Walt Disney Imagineering"},
  "alumniOf": {"@type": "CollegeOrUniversity", "name": "University of York"},
  "knowsAbout": [
    "Machine learning", "Computer vision", "Robotics", "Simulation",
    "Autonomous vehicles", "Quantum technologies", "Density functional theory",
    "Many-body perturbation theory"
  ],
  "sameAs": [
    "https://scholar.google.co.uk/citations?user=_LLNmaQAAAAJ&hl=en",
    "https://www.linkedin.com/in/jack-wetherell-921493158/",
    "https://www.researchgate.net/profile/Jack_Wetherell2",
    "https://github.com/JackWetherell",
    "https://patents.justia.com/inventor/jack-wetherell"
  ]
}
</script>""" % {"site": SITE_URL, "image": OG_IMAGE}


def _escape(text):
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def render_nav(current_slug):
    """Primary navigation, with the current page marked for CSS and screen readers."""
    items = []
    for page in PAGES:
        if not page["nav"]:
            continue
        current = ' aria-current="page"' if page["slug"] == current_slug else ""
        items.append(
            '        <li><a href="%s.html"%s>%s</a></li>' % (page["slug"], current, page["nav"])
        )
    return "<ul>\n%s\n      </ul>" % "\n".join(items)


def render_page(page, template):
    slug = page["slug"]
    body = (ROOT / "content" / ("%s.html" % slug)).read_text(encoding="utf-8").rstrip()
    canonical = "%s/" % SITE_URL if slug == "index" else "%s/%s.html" % (SITE_URL, slug)

    head_extra = []
    if page.get("noindex"):
        head_extra.append('<meta name="robots" content="noindex">')
    if slug == "index":
        head_extra.append(JSON_LD)

    html = template
    for key, value in {
        # Titles and descriptions land in attributes and in <title>, so they are
        # escaped here rather than being hand-escaped in the page table above.
        "title": _escape(page["title"]),
        "description": _escape(page["description"]),
        "canonical": canonical,
        "author": _escape(AUTHOR),
        "og_image": "%s/%s" % (SITE_URL, OG_IMAGE),
        "site_url": SITE_URL,
        "page_class": "page-%s" % slug,
        "nav": render_nav(slug),
        "content": body,
        "year": str(_datetime.date.today().year),
        "head_extra": "\n    ".join(head_extra),
    }.items():
        html = html.replace("{{%s}}" % key, value)

    # The 404 page is served from arbitrary URLs, so its asset and link paths
    # have to be absolute rather than relative to the requested directory.
    if page.get("absolute_urls"):
        html = re.sub(r'(href|src)="(?!https?:|mailto:|#|/)', r'\1="/', html)

    leftover = re.findall(r"\{\{(\w+)\}\}", html)
    if leftover:
        raise SystemExit("error: unresolved placeholders in %s: %s" % (slug, leftover))
    return html + "\n"


def render_sitemap():
    today = _datetime.date.today().isoformat()
    urls = []
    for page in PAGES:
        if page.get("noindex"):
            continue
        loc = "%s/" % SITE_URL if page["slug"] == "index" else "%s/%s.html" % (SITE_URL, page["slug"])
        priority = "1.0" if page["slug"] == "index" else "0.7"
        urls.append(
            "  <url>\n    <loc>%s</loc>\n    <lastmod>%s</lastmod>\n"
            "    <priority>%s</priority>\n  </url>" % (loc, today, priority)
        )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls)
        + "\n</urlset>\n"
    )


def build(check_only=False):
    template = (ROOT / "templates" / "base.html").read_text(encoding="utf-8")
    outputs = {"%s.html" % page["slug"]: render_page(page, template) for page in PAGES}
    outputs["sitemap.xml"] = render_sitemap()

    stale = []
    for name, text in sorted(outputs.items()):
        path = ROOT / name
        if path.exists() and path.read_text(encoding="utf-8") == text:
            continue
        stale.append(name)
        if not check_only:
            path.write_text(text, encoding="utf-8")

    if check_only:
        if stale:
            print("out of date: %s\nrun: python3 build.py" % ", ".join(stale))
            return 1
        print("all %d files up to date" % len(outputs))
        return 0

    print("built %d files (%d changed)" % (len(outputs), len(stale)))
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true", help="report stale output instead of writing it"
    )
    sys.exit(build(check_only=parser.parse_args().check))
