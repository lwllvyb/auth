''' 用于查询数据库中的所有用户 '''
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from server import User

# 创建数据库引擎，指向你的数据库文件
engine = create_engine('sqlite:////tmp/test.db', echo=True)

# 创建session
Session = sessionmaker(bind=engine)
session = Session()

# 查询所有用户
users = session.query(User).all()

# 打印用户详细信息
for user in users:
    print(f"ID: {user.id}, Username: {user.username}, Password: {user.password}")

session.close()
