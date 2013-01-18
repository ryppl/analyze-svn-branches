# See http://www.alarmchang.com/wiki/index.php?title=How_to_use_SVN_python_module(like_svn.fs%2C_svn.delta%2C_svn.repos%2C_svn.core)
"""
Program Aim : to put thing in order SVN for python module that I crack from mailer.py
2008/2/23
"""
import os
import sys
import time
 
import svn.fs
import svn.delta
import svn.repos
import svn.core
 
class SVN_To_DB:
        strSvnVer = ""
        strAuthor = ""
        strStatus = ""
        strFileName = ""
        strFullPath = ""
        dtSVN = ""
        strLog = ""
        def __init__(self):
                pass
 
def main(pool, cmd, config_fname, repos_dir, cmd_args):
        if cmd == 'commit':
                Debug = True
                records = []
                revision = int(cmd_args[0])
                repos = Repository(repos_dir, revision, pool)
                record = SVN_To_DB()
                record.strAuthor = repos.author #get Author's name
                record.strLog = repos.get_rev_prop(svn.core.SVN_PROP_REVISION_LOG) #get Commit's log
                print "Commit Log :", repos.get_rev_prop(svn.core.SVN_PROP_REVISION_LOG)
                strDateTime = repos.get_rev_prop(svn.core.SVN_PROP_REVISION_DATE) #get Commit date
                print "Commit date :", repos.get_rev_prop(svn.core.SVN_PROP_REVISION_DATE)
                print "Formated Commit date: ", time.ctime(svn.core.secs_from_timestr(repos.get_rev_prop(svn.core.SVN_PROP_REVISION_DATE), pool))
                #Start My date Format look like this "2008-02-23T15:11:41"
                strDateTime = strDateTime.split('.')
                record.dtSVN = strDateTime[0]
                print "My date format :", record.dtSVN
                #End My date Format
                records.append(record)
                messenger = Commit(pool, repos, records)
                if Debug == True:
                        for x in records:
                                print "--------infomation all in here-------------------------------"
                                x.strAuthor = records[0].strAuthor #!!Author always get one copy in one commit
                                                                                        #not retrieve from list of "records"
                                print "strAuthor: ", x.strAuthor
                                print "strStatus: ", x.strStatus
                                print "strFileName: ", x.strFileName
                                print "strFullPath: ", x.strFullPath
                                x.dtSVN = records[0].dtSVN
                                print "dtSVN: ", x.dtSVN
                                x.strLog = records[0].strLog
                                print "strLog: ", x.strLog
class Repository:
        "Hold roots and other information about the repository."
 
        def __init__(self, repos_dir, rev, pool):
                self.repos_dir = repos_dir
                self.rev = rev
                self.pool = pool
                self.repos_ptr = svn.repos.open(repos_dir, pool)
                self.fs_ptr = svn.repos.fs(self.repos_ptr)
 
                self.roots = { }
 
                self.root_this = self.get_root(rev)
 
                self.author = self.get_rev_prop(svn.core.SVN_PROP_REVISION_AUTHOR)
 
        def get_rev_prop(self, propname):
                return svn.fs.revision_prop(self.fs_ptr, self.rev, propname, self.pool)
 
        def get_root(self, rev):
                try:
                        return self.roots[rev]
                except KeyError:
                        pass
                root = self.roots[rev] = svn.fs.revision_root(self.fs_ptr, rev, self.pool)
                return root
 
class Commit:
        def __init__(self, pool, repos, records):
                # get all the changes and sort by path
                debug = True
                self.pool = pool
                self.repos = repos
                editor = svn.repos.ChangeCollector(repos.fs_ptr, repos.root_this, self.pool)
                e_ptr, e_baton = svn.delta.make_editor(editor, self.pool)
                svn.repos.replay(repos.root_this, e_ptr, e_baton, self.pool)
 
                self.changelist = editor.get_changes().items()
                self.changelist.sort()
                if debug == True:
                        #List every info that I can find from SVN DB
                        print "self.changelist : ", self.changelist
                        print "Path in changelist: ", self.changelist[0][0]
                        print "changelist item_kind: ", self.changelist[0][1].item_kind
                        '''
                        changelist[0][1].item_kind == 1 <= "item_kind = 1 meaning file"
                        changelist[0][1].item_kind == 2 <= "item_kind = 2 meaning folder"
                        '''
                        print "changelist text_changed: ", self.changelist[0][1].text_changed
                        print "changelist base_path: ", self.changelist[0][1].base_path
                        print "changelist base_rev: ", self.changelist[0][1].base_rev
                        print "changelist path: ", self.changelist[0][1].path #To know the modify file path
                        print "prop_changes",  self.changelist[0][1].prop_changes
                        print "added",  self.changelist[0][1].added
 
                #start to read commit action
                """
                Action explain
                if        : change.added = Trun "meaning New file"
                else if :
                                change.added == False and
                                change.path == None "meaning remove file"
                else if :
                                change.added== False and 
                                change.path != None "meaning modify file"
                """
                for x in self.changelist:
                        record = SVN_To_DB() #save SVN data base data to data struct
                        if x[1].added == True:
                                record.strStatus = "NEW"
                                #write result to data structure this item is New action
                        elif x[1].path == None:
                                record.strStatus = "Delete"
                                #write result to data structure this item is remove action
                        else:
                                record.strStatus = "Modify"
                                #write result to data structure this item is Modify action
 
                        record.strFullPath = x[0]
                        FileName = x[0]
                        FileName = FileName.split('/')
                        record.strFileName = FileName[-1]
                        record.strSvnVer = sys.argv[3]
                        records.append(record)
 
if __name__ == '__main__':
        scriptname = os.path.basename(sys.argv[0])
        cmd_list = {'commit'     : 1,
                    'propchange' : 3,
                    'propchange2': 4,
                    'lock'       : 1,
                    'unlock'     : 1,
                    }
 
        config_fname = None
        argc = len(sys.argv)
        cmd = sys.argv[1]
        repos_dir = svn.core.svn_path_canonicalize(sys.argv[2])
        try:
                expected_args = cmd_list[cmd]
        except KeyError:
                print "parameter wrong ~ ~", cmd
 
        svn.core.run_app(main, cmd, config_fname, repos_dir,sys.argv[3:3+expected_args])
        """
        What is this command doing ? => argv[3:3+expected_args]
        if user input command : python Mdx_SVN_fun.py commit C:/SVN_TEST/SVN_TEST 3
        this function "argv[3:3+expected_args]" will retrieve version number "3" for you!!
        """
        #x = sys.argv[3:3+expected_args]
        #print "sys.argv[3:3+expected_args] :", x
