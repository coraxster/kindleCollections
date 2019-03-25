#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# coding=utf-8

import argparse
import os
import json
import hashlib
import datetime
import struct
import unicodedata


class Sectionizer:
    def __init__(self, fn, perm):
        self.f = open(fn, perm)
        header = self.f.read(78)
        self.ident = header[0x3C:0x3C+8]
        if self.ident != b'BOOKMOBI':
            raise ValueError('invalid file format')
        num_sections, = struct.unpack_from('>H', header, 76)
        sections = self.f.read(num_sections*8)
        self.sections = struct.unpack_from('>%dL' % (num_sections*2), sections, 0)[::2] + (0xfffffff, )

    def load_section(self, section):
        before, after = self.sections[section:section+2]
        self.f.seek(before)
        return self.f.read(after - before)


def get_mobi_asin(file_path):
    try:
        sections = Sectionizer(file_path, 'rb')
        header = sections.load_section(0)
        len_mobi = struct.unpack_from('>L', header, 20)[0] + 16
        len_exth, = struct.unpack_from('>L', header, len_mobi + 4)
        exth_records = header[len_mobi:len_mobi + len_exth][12:]
        exth = dict()
        while len(exth_records) > 8:
            rectype, reclen = struct.unpack_from('>LL', exth_records)
            recdata = exth_records[8:reclen]
            exth[rectype] = recdata
            exth_records = exth_records[reclen:]
        if 113 in exth:
            return exth[113].decode("utf-8")
        return ""
    except BaseException as e:
        print(e)
        return ""


parser = argparse.ArgumentParser()
parser.add_argument('--kindleDir', default='/Volumes/Kindle')
rootDir = parser.parse_args().kindleDir.rstrip('/')
documentsDir = rootDir + '/documents/'
collectionsPath = rootDir + "/system/collections.json"

with open(collectionsPath, encoding='utf8') as json_data:
    oldCollections = json.load(json_data)

dirs = [name for name in os.listdir(documentsDir) if os.path.isdir(os.path.join(documentsDir, name))]

newCollections = {}
for d in dirs:
    colName = d + '@en-US'
    newCollections[colName] = {'lastAccess': 0, 'items': []}
    files = [name for name in os.listdir(documentsDir+'/'+d) if os.path.isfile(os.path.join(documentsDir+'/'+d, name))]
    for f in files:
        path = unicodedata.normalize('NFC', '/mnt/us/documents/' + d + '/' + f)
        filename, file_extension = os.path.splitext(f)
        if file_extension.lower() == '.mobi':
            asin = get_mobi_asin(documentsDir + d + '/' + f)
            if asin == "":
                newCollections[colName]['items'].append('*' + hashlib.sha1(path.encode('utf-8')).hexdigest())
            else:
                newCollections[colName]['items'].append('#' + get_mobi_asin(documentsDir + d + '/' + f) + '^EBOK')
        elif file_extension.lower() == '.pdf':
            newCollections[colName]['items'].append('*' + hashlib.sha1(path.encode('utf-8')).hexdigest())
        else:
            print('No book ext: ' + f)

os.rename(collectionsPath, collectionsPath + '.BU.' + datetime.datetime.now().strftime("%d-%m-%y-%H:%M:%S"))
with open(collectionsPath, 'w') as outfile:
    json.dump(newCollections, outfile)

print('Done!')
