from flask import Flask, render_template, request
import pymysql
import pandas as pd

# db connection
conn = pymysql.connect(host="ppam.ceubmhz1zgkv.ap-northeast-1.rds.amazonaws.com",user = "admin",password ="ppam1234", db="ppam_test",charset="utf8")
curs = conn.cursor(pymysql.cursors.DictCursor)

app = Flask(__name__, template_folder='templates')


@app.route('/', methods=['GET'])
def hello_world():
    post_table = pd.read_sql("select * from post_table_with_review", conn)
    post_code = list(post_table['post_code'])
    image_name = list(post_table['image_name'])
    post_name = list(post_table['post_name'])
    company_list = list(post_table['product_name'])
    # company_table = pd.read_csv('static/companycode.csv', encoding='cp949')
    # code_list = list(company_table['code'])
    # company = list(company_table['company'])
    # company_list = []
    # for post in post_code:
    #     for index, code in enumerate(code_list):
    #         if code_list[index] == post[0]:
    #             company_list.append(company[index])
    print(len(post_code))
    print(len(company_list))

    return render_template('home-page2.html', path='static/img/product_img/', postcode_list=post_code, img_list=image_name, post_list=post_name, post_len=len(post_code), company_list=company_list)


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
    company_table = pd.read_csv('static/companycode.csv', encoding='cp949')
    code_list = list(company_table['code'])
    company = list(company_table['company'])
    company_list = []
    for post in post_code:
        for index, code in enumerate(code_list):
            if code_list[index] == post[0]:
                company_list.append(company[index])
    print('찾은 상품 수 : ', len(post_code))

    return render_template('home-page2.html', path='static/img/product_img/', postcode_list=post_code, img_list=image_name, post_list=post_name, post_len=len(post_code),company_list=company_list)


# 제품별 상세페이지 띄우기
@app.route('/specific', methods=['GET'])
def load_specific_page():
    args_dict = request.args.to_dict()
    post_code = args_dict['product']

    # 제품 기본 정보 가져오기
    select_query = "select post_name, post_url, post_table_with_review.size, material, post_table_with_review.type, product_name\
                    from post_table_with_review where post_code = " + "'" + post_code + "'"
    post_table = pd.read_sql(select_query, conn)
    post_name = post_table['post_name'][0]
    post_url = post_table['post_url'][0]
    company_name = post_table['product_name'][0]
    size = post_table['size'][0]
    material = post_table['material'][0]
    type = post_table['type'][0]

    # # 제조사 가져오기
    # company_table = pd.read_csv('static/companycode.csv', encoding='cp949')
    # code_list = list(company_table['code'])
    # company = list(company_table['company'])
    # for index, code in enumerate(code_list):
    #     if code_list[index] == post_code[0]:
    #         company_name = company[index]

    # 제품 리뷰 가져오기
    select_query = "select * from review_table where review_code like " + "'" + post_code + "-%'"
    print(select_query)
    review_table_ori = pd.read_sql(select_query, conn)
    # 최신순 정렬
    review_table = review_table_ori.sort_values(by='review_date', axis=0, ascending=False)
    # 중복 제거
    review_table = review_table.drop_duplicates('review_raw', keep='last')
    date_list = list(review_table['review_date'])
    review_list = list(review_table['review_raw'])
    review_len = len(review_table)

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

        # 키워드 말 바꾸기
        for i in range(len(kwlist)):
            try:
                kwlist[i] = kwlist[i].replace("얇", "얇음")
                kwlist[i] = kwlist[i].replace("재구", "재구매")
                kwlist[i] = kwlist[i].replace("쓸리는", "쓸림")
                kwlist[i] = kwlist[i].replace("쓸리", "쓸림")
            except:
                pass

        # 해당 키워드를 포함하는 리뷰 가져오기
        select_query = "select rk.*, r.review_raw, r.review_date from review_keyword_table rk join review_table r \
                        on rk.review_code = r.review_code where r.review_code like " + "'" + post_code + "-%'"
        review_keyword_table = pd.read_sql(select_query, conn)

        def review_for_kw(kw):
            flag = review_keyword_table[kw] == '1'
            reviews = list(review_keyword_table[flag]['review_raw'])
            dates = list(review_keyword_table[flag]['review_date'])
            review_for_kw_list = [(x, y) for x, y in zip(dates, reviews)]
            return review_for_kw_list

        review_for_kw1 = review_for_kw('keyword1')
        review_for_kw2 = review_for_kw('keyword2')
        review_for_kw3 = review_for_kw('keyword3')
        review_for_kw4 = review_for_kw('keyword4')
        review_for_kw5 = review_for_kw('keyword5')
        list1_len = len(review_for_kw1)
        list2_len = len(review_for_kw2)
        list3_len = len(review_for_kw3)
        list4_len = len(review_for_kw4)
        list5_len = len(review_for_kw5)

    else:
        kwlist = None
        review_for_kw1 = None
        review_for_kw2 = None
        review_for_kw3 = None
        review_for_kw4 = None
        review_for_kw5 = None
        list1_len = None
        list2_len = None
        list3_len = None
        list4_len = None
        list5_len = None

    # 제품 성분 리스트 불러오기
    sql = "select * from post_component_table where post_code = " + "'" + post_code + "'"
    post_component_table = pd.read_sql(sql, conn)
    component_list = []
    for i in range(1,21):
        # null 값이 아닐 경우에만 리스트에 추가
        if post_component_table['component'+str(i)][0] != "":
            component_list.append(post_component_table['component'+str(i)][0])

    # 성분별 설명 및 유해정보 불러오기
    component = "("
    for index, c in enumerate(component_list):
        component += "'" + c + "'"
        if index < len(component_list)-1:
            component += ','
    component += ")"
    # 해당 제품에 있는 성분만 테이블로 불러오기
    sql = "select * from components_analysis_table where components in " + component
    component_analysis_table = pd.read_sql(sql, conn)
    component_list = list(component_analysis_table['components'])
    text_list = []
    for i in range(len(component_analysis_table)):
        temp = []
        temp.append(component_analysis_table['text'][i].replace("x"," "))
        harzards = ""
        for j in range(1,9):
            harzard_code = component_analysis_table['col'+str(j)][i]
            print(harzard_code)
            if 'H' in harzard_code:
                sql = "select harzard_text from harzard_code_table where harzard_code =" + "'" + harzard_code + "'"
                harzard_text = pd.read_sql(sql, conn)['harzard_text'][0]
                harzards += harzard_text + ", "
                print(harzard_text)
        temp.append(harzards)
        text_list.append(temp)

    return render_template('product-page2.html', post_code=post_code, post_name=post_name, post_url=post_url, \
                           size=size, material=material, type=type,\
                           kwlist=kwlist, date_list=date_list, review_list=review_list, review_len=review_len, \
                           review_for_kw1=review_for_kw1, review_for_kw2=review_for_kw2, review_for_kw3=review_for_kw3, \
                           review_for_kw4=review_for_kw4, review_for_kw5=review_for_kw5, \
                           list1_len=list1_len, list2_len=list2_len, list3_len=list3_len, list4_len=list4_len, list5_len=list5_len,\
                           company_name=company_name, component_list=component_list, component_len=len(component_list), text_list=text_list)


# 검색기능 구현하기
@app.route('/search', methods=['GET'])
def search():
    url = request.url
    search_query = url.split('?')[1].split('=')[1]
    post_table = pd.read_sql("select * from post_table_with_review where post_name like " + "'%" + search_query + "%'", conn)
    post_code = list(post_table['post_code'])
    image_name = list(post_table['image_name'])
    post_name = list(post_table['post_name'])
    company_table = pd.read_csv('static/companycode.csv', encoding='cp949')
    code_list = list(company_table['code'])
    company = list(company_table['company'])
    company_list = []
    for post in post_code:
        for index, code in enumerate(code_list):
            if code_list[index] == post[0]:
                company_list.append(company[index])
    print(len(post_code))
    print(len(company_list))

    return render_template('home-page2.html', path='static/img/product_img/', postcode_list=post_code,
                           img_list=image_name, post_list=post_name, post_len=len(post_code), company_list=company_list)


if __name__ == '__main__':
    app.run()
