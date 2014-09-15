import bs4
import datetime

def parse_datetime( date_str ):
    date = [int(i) for i in date_str.split()[0].split(".") ]
    time = [int(i) for i in date_str.split()[1].split(":")]
    return datetime.datetime(*list(reversed(date)) + time)


class Assignment:
    def __init__(self, due_datetime, handin, courseid, coursename, name, url=None, handin_time=None):
        self.due_datetime = due_datetime
        self.handin = handin
        self.handin_time = handin_time
        self.courseid = courseid
        self.coursename = coursename
        self.name = name
        self.url = url


    @classmethod
    def parse_html(cls, html):
        soup = bs4.BeautifulSoup(html)
        return cls.parse_bs4_element(soup.tr)

    @classmethod
    def parse_bs4_element(cls, tag):
        return cls.parse_attr_list([i.get_text() for i in tag if i!='\n'])

    @classmethod
    def parse_attr_list(cls, attr_list):
        due_datetime = parse_datetime( attr_list[0] )

        if attr_list[1][:4] == "Skil":
            handin = True
            handin_date= parse_datetime( attr_list[1].split(maxsplit=1)[1] )
        else:
            handin= False
            handin_date= None
        if len(attr_list) > 5:
            return cls(due_datetime, handin, attr_list[2], attr_list[3],
                        attr_list[4], url=attr_list[5], handin_time=handin_date)
        else:
            return cls(due_datetime, handin, attr_list[2], attr_list[3],
                        attr_list[4], handin_time=handin_date)

    def print_row(self, num, width=16, strft="%d.%m.%Y %H:%M"):
        print("{} {} {} {} {}".format(
            "({})".format(num).ljust(4),
            self.due_datetime.strftime(strft).ljust(width),
            u'Óskilað' if not self.handin else u'Skilað {}'.format(self.handin_time.strftime(strft)).ljust(int(width*1.5)),
            self.courseid.ljust(int(width*0.7)),
            self.name.ljust(width)))
