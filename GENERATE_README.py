#-*- coding:utf-8 -*-
import sys
import os
import os.path
import codecs
import urllib

PARSE_URL = "http://chinapub.duapp.com/gen_md?src="
GITHUB_BASE_URL = "https://raw2.github.com/zyxstar/markdown_note/master/docs"


def build_one_file(folders, filename):
    _note_path = "/".join(
        [urllib.quote_plus(_path.encode('utf-8')) for _path in folders + [filename]])
    _note_url = "%s/%s" % (GITHUB_BASE_URL, _note_path)
    return "- [%s](%s%s)" % (filename, PARSE_URL, urllib.quote_plus(_note_url))


def yield_subfiles():
    _docs_dir = os.path.join(os.path.dirname(__file__), './docs/')
    _sys_encoding = sys.getfilesystemencoding()
    def _find_subfiles(*folders):
        _folder_path = os.path.join(_docs_dir, '/'.join(folders))
        for _dirpath, _dirnames, _filenames in os.walk(_folder_path):
            for _f in _filenames:
                yield map(lambda _fo: _fo.decode(_sys_encoding), folders), _f.decode(_sys_encoding)
            for _d in _dirnames:
                _folders = list(folders)
                _folders.append(_d)
                for _a, _b in _find_subfiles(*_folders):
                    yield _a, _b
            break
    return _find_subfiles()


def build_subfiles(iter_subfiles):
    _marks = []
    _lines = ["# Manual"]
    for _folders, _filename in yield_subfiles():
        if len(_folders) and not _folders[-1] in _marks:
            _lines.append("\n%s %s" %
                          ("#" * len(_folders), _folders[-1]))
            _marks.append(_folders[-1])
        _lines.append(build_one_file(_folders, _filename))
    return _lines


def write_readme(line_list):
    with codecs.open('README.md', 'w', 'utf-8') as _f:
        _f.writelines('\r\n'.join(line_list))


if __name__ == '__main__':
    write_readme(build_subfiles(yield_subfiles()))