from flask import Flask, render_template, request
import pymysql
import pandas as pd

# db connection
conn = pymysql.connect(host="ppam.ceubmhz1zgkv.ap-northeast-1.rds.amazonaws.com",user = "admin",password ="ppam1234", db="ppam_test",charset="utf8")
curs = conn.cursor(pymysql.cursors.DictCursor)

app = Flask(__name__, template_folder='templates')


'''
1. 상품 목록 
- indexoutoferror 해결하기 (상품 없거나 배열할 개수 부족할 때 처리)

2. 필터링 검색
- 조건 여러개 일 때 post_table에서 해당 상품 목록 가져오기 -> 쿼리문? 

3. 상세페이지로 이동
- 인자 받아서 product-page2.html 변수로 전달 (제품 사진/ 상세페이지 사진/ ... 
- postcode 넘기면 리뷰 / 키워드 조회할 때 연결할 수 있다 

4. 키워드 버튼, 리뷰 띄우기 

5. 제품별 성분분석표 페이지 
'''


@app.route('/')
def hello_world():
    post_table = pd.read_sql("select * from post_table_with_review", conn)
    post_code = list(post_table['post_code'])
    image_name = list(post_table['image_name'])
    post_name = list(post_table['post_name'])
    for i in image_name:
        print('static/img/product_img/' + i)
    return render_template('home-page2.html', path='static/img/product_img/', postcode_list=post_code, img_list=image_name, post_list=post_name)


# filters: size, material, type
# x: 팬티라이너/소형/중형/대형/오버나이트/울트라  순면/한방/기타  날개형/일반형
# @app.route('/<filters>/<x>')
# def load_data(filters, x):
#     # 검색어 테이블에서 review_table 불러오기
#     post_table = pd.read_sql("select * from post_table_with_review", conn)
#     if filters is None:
#         filter_table = post_table
#     else:
#         filtering = post_table[filters] == x
#         filter_table = post_table[filtering]
#     image_name = list(filter_table['image_name'])
#     post_name = list(filter_table['post_name'])
#     for i in image_name:
#         print('static/img/product_img/' + i)
#     # return render_template('filter-table.html', tables=[filter_table.to_html(classes='data', header='true')])
#     return render_template('filter-page.html', path='static/img/product_img/', img_list=image_name, post_list=post_name)


# 체크박스 필터링 검색 구현
@app.route('/product-filtering', methods=['GET'])
def product_filtering():
    post_table = pd.read_sql("select * from post_table_with_review", conn)

    # url에서 option 정보 가져오기
    args_dict = request.args.to_dict()
    filter = args_dict['size']
    filtering = post_table['size'] == filter
    filter_table = post_table[filtering]
    post_code = list(post_table['post_code'])
    image_name = list(filter_table['image_name'])
    post_name = list(filter_table['post_name'])
    return render_template('home-page2.html', path='static/img/product_img/', postcode_list=post_code, img_list=image_name, post_list=post_name)


# 제품별 상세페이지 띄우기
@app.route('/specific', methods=['GET'])
def load_specific_page():
    post_table = pd.read_sql("select * from post_table_with_review", conn)

    args_dict = request.args.to_dict()
    post_code = args_dict['product']
    print(post_code)

    # 상세페이지 띄우기 위해 필요한 postcode, postname 인자 넘겨주기
    return render_template('product-page2.html')



if __name__ == '__main__':
    app.run()
