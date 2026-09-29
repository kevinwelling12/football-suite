"""Build the Family Club Draft page: python3 scripts/affinity/family/build.py [out.html]
Clubs come from clubs.json (254 clubs from data/suite_data.json plus research blurbs)."""
import pathlib, sys
here = pathlib.Path(__file__).parent
out = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else here / 'page.html'
out.write_text((here / 'page.template.html').read_text().replace('__CLUBS__', (here / 'clubs.json').read_text()))
print('wrote', out)
