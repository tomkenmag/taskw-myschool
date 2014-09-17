#! /usr/bin/python3
from taskw import TaskWarrior
from myschool_student import *
import re

if __name__=="__main__":
    tw = TaskWarrior()
    assignment_list = get_assignment_list()
    tasks = tw.load_tasks()['pending']
    for asg in assignment_list:
        if asg.handin:
            continue
        courseid = asg.courseid[6:]
        taskdescr = '{}: {}'.format(courseid, asg.name)
        if not any([taskdescr in t.values() for t in tasks]):
            tw.task_add( taskdescr,
                        project='homework:'+courseid,
                        due=asg.due_datetime )
            print("Task due: {}".format(int(asg.due_datetime.timestamp())))
            print("taskw: Adding task \"{}\"".format(taskdescr))
        elif asg.handin:
            print("taskw: Moving task \"{}\" completed.".format(taskdescr))
            tw.task_done(task)
