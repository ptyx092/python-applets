#!/usr/bin/python2
# coding: utf-8

import os
import glob
import sys
import tempfile
import shutil

def usage():
    
    """App usage."""
    
    appName = sys.argv[0]
    print 'Usage: ' + appName + ' dir/file extension [prefix]'
    print 'Example: ' + appName + ' ./  png bg'
    print 'This app will rename matched files with [prefix] number (1, 2, 3, ...) according to file\'s modify time'
    
def renameFiles(adir, ext, prefix = ''): #根据文件修改时间排序重命名为数字
    
    """Rename files with number according to modify time"""
    
    pattern = adir + r'/*.' + ext
    files = glob.glob(pattern)
    
    #没有匹配文件，打印信息
    if len(files) <= 0:
        print 'no matched files found in dir: ',adir
        return
    
    #统计文件mtime，创建映射表
    time2file = {}
    file2time = {}
    for afile in files:
        mtime = os.stat(afile).st_mtime
        time2file[mtime] = afile
        file2time[afile] = mtime
        
    #同时创建一个逆映射，方便使用    
    keysOfTime = time2file.keys()
    
    #将mtime进行本地排序
    keysOfTime.sort()
    
    #遍历进行重命名
    for index, mtime in enumerate(keysOfTime):
        
        #分解文件名相关信息
        afile = time2file[mtime] #从时间到文件映射取值
        path,name = os.path.split(afile)
        pre,extR = os.path.splitext(name)
        newName = prefix + str(index + 1) + extR
        
        #要命名的名称与本来名字相同，那就不用往下了
        if name == newName:
            print name,' == ',newName, ' do nothing '
            continue
        
        #组合新名字
        newFile = os.path.join(path, newName)
        
        if os.path.exists(newFile): #如果这个文件存在，那么它也应该在字典中，因为后缀一致
            swapFiles(afile, newFile) #交换这两个文件
            
            #由于交换了文件，两个映射表的信息也需交换
            anotherTime = file2time[newFile]
            time2file[mtime] = newFile
            time2file[anotherTime] = afile 
            
            file2time[newFile] = mtime
            file2time[afile] = anotherTime
        else:
            print 'rename file ', afile, ' to ', newFile
            try:
                os.rename(afile, newFile)
                
                #重命名了文件，两个映射表也需更新
                del file2time[afile]
                file2time[newFile] = mtime
                time2file[mtime] = newFile
                
            except:
                print 'rename file ', afile,' to ', newFile, ' error'
    
        
def swapFiles(file1, file2): #交换过程需确保mtime信息不变，因为我们根据mtime顺序来重命名文件的
    
    """swap two files, keep the stat state"""
    
    tempDir = tempfile.mkdtemp() #创建临时目录存储中间文件
    shutil.copy2(file1, tempDir) #复制文件的同时，保留mtime等stat信息
    
    try:
        os.rename(file2, file1) #重命名文件会删除已存在的文件file1
        shutil.copy2(os.path.join(tempDir, os.path.basename(file1)), file2)
        print 'swap ', file1, ' and ', file2
    except:
        print 'swap files error'
        
    shutil.rmtree(tempDir) #删除临时目录及其下面的文件
        
def main():
    
    """main entry"""
    
    argc = len(sys.argv)
    if argc == 3:
        renameFiles(sys.argv[1], sys.argv[2])
    elif argc == 4:
        renameFiles(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        usage()
    
if __name__ == '__main__':
    main()
