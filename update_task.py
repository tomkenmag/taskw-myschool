#! /usr/bin/python3
from taskw import TaskWarrior
from myschool_student import *
import re

if __name__=="__main__":
    tw = TaskWarrior()
    assignment_list = get_assignment_list()
    for asg in assignment_list:
        if asg.handin:
            continue
        courseid = asg.courseid[6:]
        taskdescr = '{}: {}'.format(courseid, asg.name)
        searchptrn = re.sub(r"(?<=\s)(\d+)(?=\s|$)", r"-\1", taskdescr)
        task = tw.get_task(description=searchptrn)
        task = task[1]
        if not task:
            tw.task_add( taskdescr,
                        {'project' : 'homework:'+courseid,
                         'due' : asg.due_datetime })
        elif task['status'] == 'pending' and asg.handin:
            tw.task_done(task)


