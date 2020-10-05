from flask import Flask, render_template
import pymysql
import pandas as pd

# db connection
conn = pymysql.connect(host="ppam.ceubmhz1zgkv.ap-northeast-1.rds.amazonaws.com",user = "admin",password ="ppam1234", db="ppam_test",charset="utf8")
curs = conn.cursor(pymysql.cursors.DictCursor)

app = Flask(__name__, template_folder='templates')


@app.route('/')
def hello_world():
    post_table = pd.read_sql("select * from post_table_with_review", conn)
    image_name = list(post_table['image_name'])
    post_name = list(post_table['post_name'])
    return render_template('home-page2.html', path='static/img/product_img/', img_list=image_name, post_list=post_name)


# filters: size, material, type
# x: 팬티라이너/소형/중형/대형/오버나이트/울트라  순면/한방/기타  날개형/일반형
@app.route('/<filters>/<x>')
def load_data(filters, x):
    # 검색어 테이블에서 review_table 불러오기
    post_table = pd.read_sql("select * from post_table_with_review", conn)
    if filters is None:
        filter_table = post_table
    else:
        filtering = post_table[filters] == x
        filter_table = post_table[filtering]
    image_name = list(filter_table['image_name'])
    post_name = list(filter_table['post_name'])

    # return render_template('filter-table.html', tables=[filter_table.to_html(classes='data', header='true')])
    return render_template('filter-page.html', path='static/img/product_img/', img_list=image_name, post_list=post_name)


if __name__ == '__main__':
    app.run()
