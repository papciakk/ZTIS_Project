import pickle

import MySQLdb

db = MySQLdb.connect(user="root",
                     db="salon24",
                     host="localhost",
                     password="1234",
                     charset="utf8")
c = db.cursor()

c.execute("""
    SELECT u1.login, u2.login, year(comment.datetime) FROM note
    inner join blog on note.blog_id = blog.id
    inner join user u1 on u1.id = blog.user_id
    inner join comment on comment.note_id = note.id
    inner join user u2 on u2.id = comment.user_id
""")
relation = c.fetchall()
# relation = [r for r in relation if r[0] is not None and r[1] is not None]
# relation.sort()

with open("blog_commentators_datetime.dat", "wb") as f:
    pickle.dump(relation, f)
