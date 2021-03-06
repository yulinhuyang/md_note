#-*- coding:utf-8 -*-
import sys
import os
import os.path
import codecs
import urllib
import re

SYS_ENCODING = sys.getfilesystemencoding()
PARSE_URL = "http://doc.pigfeet.cn/gen_md?src="
# GITHUB_BASE_URL = "https://raw.githubusercontent.com/zyxstar/md_note/master/docs"
GITHUB_BASE_URL = "https://code.aliyun.com/zyxstar2013/md_note/raw/master/docs"

ORDER_DIC = {"Analysis":10,
             "Design":15,
             "OS":20,
             "Language":30,
             "Skill":40,
             "Framework":50,
             "RubyProgramming.md":10,
             "RubyPlatform.md":20,
             "PythonCookBook.md":10,
             u"编程范式(stanford_cs107).md".encode(SYS_ENCODING):10,
             u"需求分析训练营(徐锋).md".encode(SYS_ENCODING):10,
             u"有效用例模式(SteveAdolph).md".encode(SYS_ENCODING):20,
             u"Linux基础(RHEL).md".encode(SYS_ENCODING):10,
             u"深入理解计算机系统(csapp).md".encode(SYS_ENCODING):10,
             u"Unix环境高级编程(apue).md".encode(SYS_ENCODING):20,
             u"ARM基础.md".encode(SYS_ENCODING):30,
             u"Git版本控制之道.md".encode(SYS_ENCODING):20,
             u"Make项目管理.md".encode(SYS_ENCODING):40,
             u"编程范式(stanford_cs107).md".encode(SYS_ENCODING):10,
             u"征服C指针(前桥和弥).md".encode(SYS_ENCODING):20,
             u"C语言(Uplooking).md".encode(SYS_ENCODING):30,
             u"JavaScript语言核心.md".encode(SYS_ENCODING):10,
             u"JavaScript语言精髓(周爱民).md".encode(SYS_ENCODING):15,
             u"JavaScript函数式介绍.md".encode(SYS_ENCODING):20,
             u"JavaScript函数式编程.md".encode(SYS_ENCODING):30,
             u"JavaScript异步编程.md".encode(SYS_ENCODING):40,
             u"JavaScript项目构建.md".encode(SYS_ENCODING):50,
             "UnitTesting.md":30,
             "DataBase.md":40,
            }


def build_one_file(folders, filename):
    def get_file__author_date():
        _path = ["./docs"] + folders + [filename]
        with codecs.open(os.path.join(*_path), 'r', 'utf-8') as _f:
            _m = re.search(r"> (\d{4}-\d{1,2}-\d{1,2})",_f.readline())
            if _m:return _m.group(1)
        return ""

    _note_path = "/".join(
        [urllib.quote_plus(_path.encode('utf-8')) for _path in folders + [filename]])
    _note_url = "%s/%s" % (GITHUB_BASE_URL, _note_path)
    return "- [%s](%s%s) <span>%s</span>" % (filename, PARSE_URL, urllib.quote_plus(_note_url), get_file__author_date())


def yield_subfiles():
    _docs_dir = os.path.join(os.path.dirname(__file__), './docs/')
    def _find_subfiles(*folders):
        _folder_path = os.path.join(_docs_dir, '/'.join(folders))
        for _dirpath, _dirnames, _filenames in os.walk(_folder_path):
            for _f in sorted(_filenames,key=lambda _file:ORDER_DIC.setdefault(_file,999)):
                yield map(lambda _fo: _fo.decode(SYS_ENCODING), folders), _f.decode(SYS_ENCODING)
            for _d in sorted(_dirnames,key=lambda _dir:ORDER_DIC.setdefault(_dir,999)):
                _folders = list(folders)
                _folders.append(_d)
                for _a, _b in _find_subfiles(*_folders):
                    yield _a, _b
            break
    return _find_subfiles()


def build_subfiles(iter_subfiles):
    _marks = []
    _lines = ["# Manual"]

    def _build_path_to_tocs(folders):
        for i in range(1, len(folders)+1):
            _folder_pieces=folders[0:i]
            if not _folder_pieces in _marks:
                _marks.append(_folder_pieces)
                _lines.append("\n%s %s" % ("#" * len(_folder_pieces), _folder_pieces[-1]))

    for _folders, _filename in yield_subfiles():
        if len(_folders):
            _build_path_to_tocs(_folders)

        _lines.append(build_one_file(_folders, _filename))
    return _lines


def write_readme(line_list):
    with codecs.open('README.md', 'w', 'utf-8') as _f:
        _f.write('\r\n'.join(line_list))
        _f.write('\r\n')
        _f.write('\r\n')
        _f.write("""<style type="text/css">li span{font-size:0.95em;color:#555;font-family:'sans-serif';padding-left:5px;}</style>""")


if __name__ == '__main__':
    write_readme(build_subfiles(yield_subfiles()))
