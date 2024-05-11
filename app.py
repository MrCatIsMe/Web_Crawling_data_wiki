from flask import Flask, render_template
import mysql.connector
from mysql.connector import Error
import requests
from bs4 import BeautifulSoup
import mysql.connector
from flask import request

app = Flask(__name__)
# Hàm crawl dữ liệu từ Wikipedia
def crawl_wikipedia():
    url = "https://en.wikipedia.org/wiki/Main_Page"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.find_all("a", href=True)
    return [link["href"] for link in links]
def get_all(query, params=None):
    conn = None
    try:
        conn = mysql.connector.connect(
            host='localhost',
            port=3306,
            database='data',
            user='root',
            password='02032003'
        )
        if conn.is_connected():
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            data = cursor.fetchall()
            return data
    except Error as e:
        print("Error while connecting to MySQL:", e)
    finally:
        if conn is not None and conn.is_connected():
            cursor.close()
            conn.close()


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def data():
    page = int(request.args.get('page', 1))
    per_page = 10  # Số mục trên mỗi trang
    offset = (page - 1) * per_page
    query = "SELECT * FROM updata LIMIT %s OFFSET %s"
    result = get_all(query, (per_page, offset))
    # Đếm số lượng trang
    total_count_query = "SELECT COUNT(*) FROM updata"
    total_count_result = get_all(total_count_query)
    total_count = total_count_result[0][0] if total_count_result else 0
    total_pages = (total_count + per_page - 1) // per_page
    return render_template('data.html', data=result, page=page, total_pages=total_pages)


@app.route('/detail/<int:item_id>')
def detail(item_id):
    query = "SELECT * FROM updata WHERE ID = %s" % item_id  # Sửa đổi ở đây
    result = get_all(query)
    if result:
        return render_template('detail.html', item=result[0])
    else:
        return "Item not found"
    
@app.route('/search/')
def search():
    keyword = request.args.get('keyword', '')  # Lấy từ khóa tìm kiếm từ query string
    query = "SELECT * FROM updata WHERE TITLE LIKE %s OR DESCRIPTION LIKE %s OR DETAIL LIKE %s"
    result = get_all(query, ('%' + keyword + '%', '%' + keyword + '%', '%' + keyword + '%'))
    return render_template('search_result.html', keyword=keyword, data=result)

if __name__ == '__main__':
    app.run(debug=True)