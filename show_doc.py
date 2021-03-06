#-*- coding:utf-8 -*-
import sys
import os
import urllib
import urlparse
import random
import SimpleHTTPServer
import threading
import subprocess


def run_notes_srv(port):
    os.chdir("F:\study\md_proj\md_note")
    subprocess.Popen("python -m SimpleHTTPServer "+ str(port))


    # t = threading.Thread(target=SimpleHTTPServer.test)
    # if len(sys.argv) == 1:
    #     sys.argv.append(str(port))
    # else:
    #     sys.argv[1] = str(port)
    # t.start()
    # return t


def trans_note_urlpara(file_path, port):
    note_srv = "http://localhost:"+str(port)
    sys_encoding = sys.getfilesystemencoding()
    file_paths = map(lambda _pa: _pa.decode(sys_encoding),
                     os.path.normpath('\\' + file_path).split('\\'))

    url_paths = "/".join([urllib.quote_plus(_path.encode("gbk"))
                         for _path in file_paths])

    p_src = urllib.quote_plus(urlparse.urljoin(note_srv, url_paths))
    p_title =urllib.quote_plus(os.path.basename(file_path).rsplit('.',1)[0].decode(sys_encoding).encode('utf-8'))
    return "src=%s&title=%s" % (p_src,p_title)


def run_md2pg_srv(port):
    os.chdir("F:\study\md_proj\md2page_with_webpy")
    subprocess.Popen("python home.py "+ str(port))

def show_doc(port,url):
    #add to path
    #C:\Users\Administrator\AppData\Local\Google\Chrome\Application\
    #C:\Program Files (x86)\Google\Chrome\Application\
    subprocess.Popen("chrome.exe http://localhost:%s/gen_md?%s#footer" % (port,url))


if __name__ == '__main__':
    file_path =sys.argv[1]
    note_srv_port = random.Random().randint(10000,32767)
    md2pg_srv_port = random.Random().randint(32738,65535)

    run_notes_srv(note_srv_port)
    run_md2pg_srv(md2pg_srv_port)

    show_doc(md2pg_srv_port,trans_note_urlpara(file_path,note_srv_port))



#usage in shell:  start .\show_doc.py .\docs\Analysis\需求分析_徐锋.md


