"""Render a complete page from JSON nodes and shared CSS presets."""
import argparse
import json
import re
import shutil
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined, TemplateError

ROOT = Path(__file__).resolve().parent
VOID_TAGS = set('area base br col embed hr img input link meta param source track wbr'.split())
TAGS = set('a abbr address article aside audio b bdi bdo blockquote body button canvas caption cite code colgroup data datalist dd del details dfn dialog div dl dt em fieldset figcaption figure footer form h1 h2 h3 h4 h5 h6 header hgroup i iframe ins kbd label legend li main map mark menu meter nav noscript object ol optgroup option output p picture pre progress q rp rt ruby s samp section select slot small span strong sub summary sup table tbody td template textarea tfoot th thead time title tr u ul var video'.split()) | VOID_TAGS


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def build(root=ROOT):
    root = Path(root).resolve()
    name = load(root.parent / 'input/config.json')['project']
    if not isinstance(name, str) or not re.fullmatch(r'[a-z][a-z0-9-]*', name):
        raise ValueError('project must be a lowercase folder name using letters, digits and hyphens')
    source = root.parent / 'input' / name
    site = load(source / 'site.json')
    page = load(source / 'page.json')
    presets = load(root / 'presets.json')
    ids = set()

    def attributes(attrs):
        if not isinstance(attrs, dict):
            raise ValueError('attrs must be an object')
        for key, value in attrs.items():
            if not re.fullmatch(r'[a-zA-Z][\w:-]*', key) or key.lower().startswith('on'):
                raise ValueError(f'Invalid attribute: {key}')
            if key.lower() == 'srcdoc':
                raise ValueError('Use JSON children instead of HTML srcdoc')
            if key.lower() in {'href', 'src', 'action', 'formaction'} and re.match(r'\s*(javascript|vbscript):', str(value), re.I):
                raise ValueError(f'Invalid URL in {key}')
            if key == 'id':
                if value in ids:
                    raise ValueError(f'Duplicate id: {value}')
                ids.add(value)

    def resolve(node):
        if not isinstance(node, dict):
            raise ValueError('Each node must be an object or a text string')
        unknown = set(node) - {'preset', 'tag', 'classes', 'attrs', 'text', 'children'}
        if unknown:
            raise ValueError(f'Unknown node fields: {sorted(unknown)}')
        base = presets[node['preset']] if 'preset' in node else {}
        return {
            'tag': node.get('tag', base.get('tag', 'div')),
            'classes': node.get('classes', base.get('classes', [])),
            'attrs': {**base.get('attrs', {}), **node.get('attrs', {})},
            'text': node.get('text', base.get('text')),
            'children': node.get('children', base.get('children', [])),
        }

    def validate(nodes):
        if not isinstance(nodes, list):
            raise ValueError('page and children must be arrays')
        for node in nodes:
            if isinstance(node, str):
                continue
            n = resolve(node)
            if n['tag'] not in TAGS:
                raise ValueError(f"Unsupported tag: {n['tag']}")
            if not isinstance(n['classes'], list) or any(not isinstance(c, str) or not re.fullmatch(r'[\w-]+', c) for c in n['classes']):
                raise ValueError('classes must be an array of CSS class names')
            if n['text'] is not None and not isinstance(n['text'], str):
                raise ValueError('text must be a string')
            attributes(n['attrs'])
            if n['tag'] in VOID_TAGS and (n['children'] or n['text'] is not None):
                raise ValueError(f"{n['tag']} cannot contain text or children")
            validate(n['children'])

    attributes(site.get('body', {}))
    site.setdefault('body', {})
    validate(page)
    css = (root / 'assets/style.css').read_text(encoding='utf-8')
    javascript = (root / 'assets/script.js').read_text(encoding='utf-8')
    theme = site.get('theme', {})
    for key, value in theme.items():
        if not re.fullmatch(r'--[\w-]+', key) or any(c in str(value) for c in '{};<>'):
            raise ValueError(f'Invalid theme variable: {key}')
    css += '\n:root {' + ''.join(f'{key}:{value};' for key, value in theme.items()) + '}'
    if '</style' in css.lower() or '</script' in javascript.lower():
        raise ValueError('Unexpected closing tag in CSS or JavaScript')
    env = Environment(loader=FileSystemLoader(root / 'templates'), autoescape=True,
                      undefined=StrictUndefined, trim_blocks=True, lstrip_blocks=True)
    env.globals.update(resolve=resolve, void_tags=VOID_TAGS)
    html = env.get_template('index.html').render(site=site, page=page, css=css, javascript=javascript)
    destination = root.parent / 'output' / name
    destination.mkdir(parents=True, exist_ok=True)
    if (source / 'assets').is_dir():
        shutil.copytree(source / 'assets', destination / 'assets', dirs_exist_ok=True)
    output = destination / 'index.html'
    output.write_text(html, encoding='utf-8')
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    try:
        print(f'Generated {build()}')
    except (ValueError, OSError, KeyError, TypeError, TemplateError) as error:
        parser.exit(1, f'Error: {error}\n')
