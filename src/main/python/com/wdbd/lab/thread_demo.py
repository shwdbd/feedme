#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   thread_demo.py
@Time    :   2023/12/08 10:44:03
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :

'''
import threading
import time
import random


# 线程操作
def thread_action(file_path, content):
    # with open(file_path, 'a') as f:
    #     f.write(content)
    print("线程{n}: {f} start".format(f=file_path, n=content))
    time.sleep(random.randint(3, 8))
    print("... ... 线程{n} ... ".format(n=content))
    time.sleep(random.randint(3, 8))
    print("线程{n}: {f} end".format(f=file_path, n=content))


def main():
    file_path = 'example.txt'
    threads = []    # 线程的集合
    for i in range(5):
        t = threading.Thread(target=thread_action, args=(file_path, f'Thread {i}'))
        threads.append(t)
        t.start()

    time.sleep(2)
    for t in threads:
        # print(t.is_alive())
        t.join()
        print("线程{n} joined ".format(n=t))

    # with open(file_path, 'r') as f:
    #     print(f.read())


if __name__ == '__main__':
    main()
