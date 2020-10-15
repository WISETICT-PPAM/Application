from flask import Flask, render_template, request
import pymysql
import pandas as pd

# db connection
conn = pymysql.connect(host="ppam.ceubmhz1zgkv.ap-northeast-1.rds.amazonaws.com",user = "admin",password ="ppam1234", db="ppam_test",charset="utf8")
curs = conn.cursor(pymysql.cursors.DictCursor)

app = Flask(__name__, template_folder='templates')


'''
키워드 버튼, 리뷰 띄우기 
탭메뉴에 전체리뷰 버튼도 있어야 할듯?

제품별 성분분석표 페이지 
'''


@app.route('/')
def hello_world():
    post_table = pd.read_sql("select * from post_table_with_review", conn)
    post_code = list(post_table['post_code'])
    image_name = list(post_table['image_name'])
    post_name = list(post_table['post_name'])
    return render_template('home-page2.html', path='static/img/product_img/', postcode_list=post_code, img_list=image_name, post_list=post_name, post_len=len(post_code))


# 체크박스 필터링 검색 구현
@app.route('/product-filtering', methods=['GET'])
def product_filtering():
    options_dict = {}
    # url에서 filter option 정보 가져오기
    url = request.url
    # http://127.0.0.1:5000/product-filtering?size=소형&size=중형
    options = url.split('?')[1].split('&')
    for option in options:
        category = option.split('=')[0]
        selected = "'" + option.split('=')[1] + "'"
        if category in options_dict:
            options_dict[category] = ",".join([options_dict[category], selected])
        else:
            options_dict[category] = selected

    select_query = ''
    for key in options_dict:
        if len(options_dict) == 1:
            options = '(' + options_dict[key] + ')'
            select_query = "select * from post_table_with_review " \
                           "where " + key + " in " + options
    if len(options_dict) == 2:
        keys = [*options_dict.keys()]
        options1 = '(' + options_dict[keys[0]] + ')'
        options2 = '(' + options_dict[keys[1]] + ')'
        select_query = "select * from post_table_with_review " \
                       "where " + keys[0] + " in " + options1 + "and " + keys[1] + " in " + options2
    if len(options_dict) == 3:
        keys = [*options_dict.keys()]
        options1 = '(' + options_dict[keys[0]] + ')'
        options2 = '(' + options_dict[keys[1]] + ')'
        options3 = '(' + options_dict[keys[2]] + ')'
        select_query = "select * from post_table_with_review " \
                       "where " + keys[0] + " in " + options1 + \
                       "and " + keys[1] + " in " + options2 + \
                       "and " + keys[2] + " in " + options3

    post_table = pd.read_sql(select_query, conn)
    post_code = list(post_table['post_code'])
    image_name = list(post_table['image_name'])
    post_name = list(post_table['post_name'])
    print('찾은 상품 수 : ', len(post_code))
    return render_template('home-page2.html', path='static/img/product_img/', postcode_list=post_code, img_list=image_name, post_list=post_name, post_len=len(post_code))


# 제품별 상세페이지 띄우기
@app.route('/specific', methods=['GET'])
def load_specific_page():
    args_dict = request.args.to_dict()
    post_code = args_dict['product']

    # 제품 기본 정보 가져오기
    select_query = "select post_name, post_url from post_table_with_review where post_code = " + "'" + post_code + "'"
    post_table = pd.read_sql(select_query, conn)
    post_name = post_table['post_name'][0]
    post_url = post_table['post_url'][0]

    # 제품 리뷰 가져오기
    select_query = "select * from review_table where review_code like " + "'" + post_code + "-%'"
    print(select_query)
    review_table = pd.read_sql(select_query, conn)
    date_list = list(review_table['review_date'])
    review_list = list(review_table['review_raw'])
    review_len = len(review_list)

    # 리뷰수 20개 넘어야만 키워드 있음
    if review_len >= 20:
        # 제품 키워드 가져오기
        select_query = "select * from keyword_table where post_code = " + "'" + post_code + "'"
        keyword_table = pd.read_sql(select_query, conn)
        kw1 = keyword_table['keyword1'][0]
        kw2 = keyword_table['keyword2'][0]
        kw3 = keyword_table['keyword3'][0]
        kw4 = keyword_table['keyword4'][0]
        kw5 = keyword_table['keyword5'][0]
        kwlist = [kw1, kw2, kw3, kw4, kw5]

        # 해당 키워드를 포함하는 리뷰 가져오기 > 구현필요
        select_query = "select * from review_keyword_table where review_code like " + "'" + post_code + "-%'"
        review_keyword_table = pd.read_sql(select_query, conn)
    else:
        kwlist = None

    return render_template('product-page2.html', post_code=post_code, post_name=post_name, post_url=post_url, kwlist=kwlist, date_list=date_list, review_list=review_list, review_len=review_len)


if __name__ == '__main__':
    app.run()
