# Copyright Dave Abrahams 2013. Distributed under the Boost
# Software License, Version 1.0. (See accompanying
# file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
#
######################################################################
#    Licensed to the Apache Software Foundation (ASF) under one
#    or more contributor license agreements.  See the NOTICE file
#    distributed with this work for additional information
#    regarding copyright ownership.  The ASF licenses this file
#    to you under the Apache License, Version 2.0 (the
#    "License"); you may not use this file except in compliance
#    with the License.  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing,
#    software distributed under the License is distributed on an
#    "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
#    KIND, either express or implied.  See the License for the
#    specific language governing permissions and limitations
#    under the License.
######################################################################

import sys
import svn.fs, svn.delta, svn.repos, svn.core
# Available change actions
from svn.repos import CHANGE_ACTION_MODIFY,CHANGE_ACTION_ADD,CHANGE_ACTION_DELETE,CHANGE_ACTION_REPLACE
from svn.core import svn_node_dir, svn_node_file
import ChangeCollector

class Repository(object):
    def __init__(self, path):
        self.repo = svn.repos.open(
            svn.core.svn_dirent_canonicalize(path))
        self.fs = svn.repos.fs(self.repo)

    def youngest_rev(self):
        return svn.fs.youngest_rev(self.fs)

class Revision(object):
    __slots__ = ('modified_tree', 'copied_tree', 'deleted_tree')
    def __init__(self, modified_tree, copied_tree, deleted_tree):
        self.modified_tree = modified_tree
        self.copied_tree = copied_tree
        self.deleted_tree = deleted_tree

def get_changeset(repo, revnum):
    root = svn.fs.revision_root(repo.fs, revnum)
    collector = ChangeCollector.ChangeCollector(repo.fs, root)
    editor, baton = svn.delta.make_editor(collector)
    svn.repos.replay(root, editor, baton)
    return collector.get_changes().items()

def log(*args, **kw):
    print '***',
    for a in args:
        print a,
    for k,v in kw.items():
        print k, '=', v

class ChangeCollector(object):
    def __init__(self, repo, root = ''):
        self.collector = ChangeCollector.ChangeCollector(repo.fs, root)
        self.editor_ptr, self.e_baton = svn.delta.make_editor(self.collector)

funky_move_revs = range(38327, 38330)

def run():
    repo = Repository(sys.argv[1])
    max_rev = repo.youngest_rev()

    # Preallocate database of revisions
    revisions = [None]*(max_rev+1)
    branches = {'trunk/boost':[], 'trunk':[]}
    for revnum in range(max_rev + 1):
        print '='*5, revnum, '='*5
        changes = get_changeset(repo, revnum)
        print 'rooted at:', (None if len(changes) == 0 else path_lcd(p for p,c in changes))
        for p, data in changes:
            import pprint
            pprint.pprint((
                    p, dict(((s,getattr(data,s)) for s in data.__slots__))
                    ))

def path_lcd(paths):
    """
>>> path_lcd(['a/b/c/d/e', 'a/b/c/q/r', 'a/b/c/f/g'])
'a/b/c'
>>> path_lcd(['apple/bear/cat', 'bob/slack'])
''
    """
    remaining_paths = iter(paths)
    lcd = remaining_paths.next().split('/') 

    for p in remaining_paths:
        elements = p.split('/')
        for n in range(min(len(lcd), len(elements))):
            if lcd[n] != elements[n]:
                lcd = lcd[:n]
                break

    return intern('/'.join(lcd))

if __name__ == '__main__':
    import doctest
    doctest.testmod()
    run()
