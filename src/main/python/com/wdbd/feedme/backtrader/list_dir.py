
import os


# 清理柯南目录
def clean_kn():
    """ 清理柯南目录 """
    root_dir = r'E:\000 名侦探柯南 1055 1092\\'
    
    files = os.listdir(root_dir)
    for f in files:
        basename = os.path.basename(f)
        (filename, p) = os.path.splitext(basename)
        if filename.find("[阳光电影-www.ygdy8.com]") == 0 and p == '.mp4':
            file_new_name = filename.replace("[阳光电影-www.ygdy8.com]", "")
            print(file_new_name)
            os.rename(root_dir+basename, root_dir+file_new_name+".mp4")


def change_name():
    """ 汉字趣谈，批量修改文件名 """
    root_dir = r'D:\000 汉字\\'
    # file_name = "汉字趣谈 水 (398) - 1.398_water_final_sc(Av763298257,P1)"
    
    files = os.listdir(root_dir)
    for f in files:
        basename = os.path.basename(f)
        (filename, p) = os.path.splitext(basename)

        s = filename.replace("_", "")
        zn_zi = s[s.find("汉字趣谈 ")+len("汉字趣谈 "):s.find("(")]
        # print(zn_zi)
        zn_no = s[s.find("(")+1: s.find(")")]
        s = filename[filename.find("-"): ][7+1 : ]
        en_zi = s[: s.find("_final_sc")]
        # print(en_zi)
        new_name = "{no} {zi} _ {en}.mp4".format(no=zn_no, zi=zn_zi.strip(), en=en_zi)
        print(new_name)
        # 改名
        os.rename(root_dir+basename, root_dir+new_name)


def list_dir():
    """ 列出文件夹下的文件名 """
    root_dir = r'D:\\000 历史研究 演讲\\'

    files = os.listdir(root_dir)
    for f in files:
        # print(f)
        # print(os.path.basename(f))
        basename = os.path.basename(f)
        (n, p) = os.path.splitext(basename)
        print(n)
    # print()
    
    
def list_kn_dir():
    """ 列出柯南文件夹下的文件名 """
    root_dir = r'D:\NAS视频\影视资料库\名侦探柯南\柯南剧集 优酷\\'

    files = os.listdir(root_dir)
    
    for f_dir in files:
        dir_path = root_dir + f_dir
        for f in os.listdir(dir_path):
            basename = os.path.basename(f)
            (n, p) = os.path.splitext(basename)
            print(n)
        
        # # print(f)
        # # print(os.path.basename(f))
        # basename = os.path.basename(f)
        # (n, p) = os.path.splitext(basename)
        # print(n)
        # print(dir_path)
    # print()



if __name__ == "__main__":
    # change_name()
    list_dir()
    # clean_kn()
    # list_kn_dir()
