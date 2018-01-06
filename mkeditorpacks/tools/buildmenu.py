#!/usr/bin/env python3
#-*- coding: UTF-8 -*-

# Copyright (c) 2014-2017, Daemon Developers
# All rights reserved.
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#  * Neither the name of the Daemon developers nor the
#    names of its contributors may be used to endorse or promote products
#    derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL DAEMON DEVELOPERS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


import yaml
import re
import sys
import os.path
from xml.etree import ElementTree as ET
from datetime import datetime
import argparse
from collections import OrderedDict


# load yaml data as ordered dict so generated file content keep the same order after each generation (reduces diff noise)
def yaml_dict_representer(dumper, data):
    return dumper.represent_dict(data.iteritems())


def yaml_dict_constructor(loader, node):
    return OrderedDict(loader.construct_pairs(node))


yaml_mapping_tag = yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG
yaml.add_representer(OrderedDict, yaml_dict_representer)
yaml.add_constructor(yaml_mapping_tag, yaml_dict_constructor)


def fine_format_xml(root):
    lines = ET.tostringlist(root, encoding='unicode')
    result = []
    prev = '>'
    for line in lines:
        if (line.startswith('<') and prev.endswith('>')) and not (line.startswith('</var>') and prev.endswith('</cond>')):
            result.append('\n')
        result.append(line)
        prev = line
    return ''.join(result)


def sort_stage_keys(stage):
    result = []
    for k, v in stage:
        if k in ('meta', 'vis', 'light', 'minimap'):
            result.insert(0, (k, v))
        else:
            result.append((k, v))
    return result


def print_gtkradiant_file(data):
    project = ET.Element('project')

    def add(name, value):
        value = str(value)
        value = value.replace('@', '$TEMPLATE')
        ET.SubElement(project, 'key', attrib={'name': name, 'value': value})

    add('version', 2)
    d = datetime.utcnow()
    tv = d.day + d.month * 32 + (d.year - 2000) * 367
    add('template_version', tv) # increase every update
    add('basepath', '@enginepath@basedir/')
    add('rshcmd', '')
    add('entitypath', '@toolspath@basedir/scripts/entities.def')
    add('texturepath', '@enginepath@basedir/textures/')
    add('autosave', '@userhomepath@basedir/maps/autosave.map') # bad. should be replaced
    add('mapspath', '@userhomepath@basedir/maps/') # bad. should be replaced

    for cmd in data:
        name = 'bsp_Q3Map2: ' + cmd['name']
        stagelist = []
        for stage in cmd['opts']:
            olist = [
                '"@apppath@q3map2"',
                '-v',
                '#',
                '-game unvanquished',
                '-fs_basepath "@enginepath"',
            ]
            for o, v in sort_stage_keys(stage.items()):
                t = '-' + o
                if v is not None:
                    t += ' {}'.format(v)
                olist.append(t)
            olist.append('$')
            stagelist.append(' '.join(olist))
        value = '! ' + ' && ! '.join(stagelist)
        add(name, value)


    print('<?xml version="1.0"?>')
    print('<!DOCTYPE project SYSTEM "dtds/project.dtd">')
    print(fine_format_xml(project))


def print_netradiant_file(data):
    project = ET.Element('project', attrib={'version': '2.0'})

    q3map2 = ET.SubElement(project, 'var', attrib={'name': 'q3map2'})
    q3map2.text = '"[RadiantPath]q3map2.[ExecutableType]" [ExtraQ3map2Args] -v'
    cond = ET.SubElement(q3map2, 'cond', attrib={'value': '[MonitorAddress]'})
    cond.text = ' -connect [MonitorAddress]'
    cond.tail = ' -game unvanquished -fs_basepath "[EnginePath]" -fs_homepath "[UserEnginePath]" '
    cond2 = ET.SubElement(q3map2, 'cond', attrib={'value': '[GameName]'})
    cond2.text = ' -fs_game [GameName]'

    for cmd in data:
        build = ET.SubElement(project, 'build', attrib={'name': cmd['name']})
        for stage in cmd['opts']:
            olist = ['[q3map2]']
            for o, v in sort_stage_keys(stage.items()):
                t = '-' + o
                if v is not None:
                    t += ' {}'.format(v)
                olist.append(t)
            olist.append('"[MapFile]"')

            command = ET.SubElement(build, 'command')
            command.text = ' '.join(olist)

    print('<?xml version="1.0"?>')
    print(fine_format_xml(project))


def create_parser():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Generates radiant q3map2 build menu file.')

    parser.add_argument('filename', metavar="buildmenu.yaml", type=argparse.FileType('r'), help='buildmenu.yaml')
    group = parser.add_argument_group(title='Radiant')
    group = group.add_mutually_exclusive_group(required=True)
    group.add_argument('-n', '--netradiant', action='store_true', help='NetRadiant')
    group.add_argument('-g', '--gtkradiant', action='store_true', help='GtkRadiant')

    return parser

args = create_parser().parse_args()
text = args.filename.read()
data = yaml.load(text)

if args.netradiant:
	print_netradiant_file(data)
elif args.gtkradiant:
	print_gtkradiant_file(data)
