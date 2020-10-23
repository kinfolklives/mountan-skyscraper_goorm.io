from django.shortcuts import render
from django.core.paginator import Paginator
import pymysql.cursors
import folium
from django.http.response import JsonResponse

# Connect to the database
connection = pymysql.connect(host='localhost',
                             user='root',
                             password='1234',
                             db='mydb',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)


# Create your views here.
def get_weather_skyscrapers(id, results_weather):
    for result in results_weather:
        if id == result['bldg_id']:
            return result
    
    result = list()
    return result
    

def skyscrapers_home(request):
    page = request.GET.get('page', '1')

    with connection.cursor() as cursor:
        # 지도에 마커 모두 출력하기
        # sql 실행
        # sql = f"""SELECT * FROM skyscrapers, bldg_images
        #           WHERE skyscrapers.id=1 AND skyscrapers.id = bldg_images.bldg_id"""
        sql = "SELECT * FROM skyscrapers"
        cursor.execute(sql)
        result = cursor.fetchall()
        result_copy = result
        # print(result)

        sql = "SELECT * FROM bldg_weather"
        cursor.execute(sql)
        results_weather = cursor.fetchall()

	    # 지도 위도, 경도 얻기
        lat_long = [result[0]['x_coord'], result[0]['y_coord']]
        m = folium.Map(lat_long, zoom_start=2)
        for countmap in range(1, 100):
            # m = folium.Map(lat_long, zoom_start=12, tiles='Stamen Terrain')
            # folium 한글깨짐 해결 방법 : 아래 명령어 실행 후 서버 재실행
            # sudo pip3 install git+https://github.com/python-visualization/branca.git@master

            # text = "<b>#"+str(countmap)+" "+result[countmap]['building_name']+"</b></br><i>"+result[countmap]['city_name']+"</i></br>"\
            #        +"<div><a href='http://localhost:8000/buildings/detail/"+str(countmap)+"'>상세히보기</a></div>" 
            # 팝업창 내용 넣기
            text = "<b>#"+str(countmap)+" "+result[countmap]['building_name']+"</b></br><i>"+result[countmap]['city_name']+"</i>"
            weather = get_weather_skyscrapers(result[countmap]['id'], results_weather)
            if weather:
                text = text + "<br> main_weather : </b>" + weather['main_weather']
                text = text + "<br> temperature : </b>" + weather['temperature_C']
                text = text + "<br> humidity : </b>" + weather['humidity']
            lat_long = [result[countmap]['x_coord'], result[countmap]['y_coord']]
            popText = folium.Html(text+str(lat_long), script=True)
            popup = folium.Popup(popText, max_width=2650)
            folium.CircleMarker(lat_long, radius=10, popup=popup, color='#3186cc',fill_color='#3186cc',).add_to(m)

        # folium HTML 얻기
        m = m._repr_html_() #updated

        # sql = "SELECT id, ranking, building_name, city_name, country, height_m FROM skyscrapers"
        # cursor.execute(sql)
        result = result_copy

        paginator = Paginator(result, 10)
        page_obj = paginator.get_page(page)

        # context = {'data':page_obj, 'bldg_map': m}

    # return render(request, 'home.html', context)
    # return render(request, 'home.html')
        context = {'bldg_data':page_obj, 'bldg_map': m}    
    return context

def home(request):
    context = skyscrapers_home(request)

    return render(request, 'home.html', context)

def maplist(request):
    context = skyscrapers_home(request)

    return render(request, 'buildings/bldg_maplist.html', context)



def bldg_list(request):
    page = request.GET.get('page', '1')

    # ranking', 'building_name', 'city_name', 'country', 'height_m', 'height_ft',
    # 'floor', 'completion_year', 'material', 'category', 'thumbnail',
    # 'x_coord', 'y_coord', 'reg_date'

    with connection.cursor() as cursor:
        sql = "SELECT id, ranking, building_name, city_name, country, height_m FROM skyscrapers"
        cursor.execute(sql)
        result = cursor.fetchall()
        paginator = Paginator(result, 10)
        page_obj = paginator.get_page(page)
        print(result)

        context = {'data':page_obj}

    return render(request, 'buildings/bldg_list.html', context)

def bldg_detail(request, id):
    with connection.cursor() as cursor:
        sql = f"""SELECT * FROM skyscrapers, bldg_images
                  WHERE skyscrapers.id={id} AND skyscrapers.id = bldg_images.bldg_id"""
        cursor.execute(sql)
        result = cursor.fetchall()
        print(result)

        lat_long = [result[0]['x_coord'], result[0]['y_coord']]
        m = folium.Map(lat_long, zoom_start=14)
        # m = folium.Map(lat_long, zoom_start=12, tiles='Stamen Terrain')

        # folium 한글깨짐 해결 방법 : 아래 명령어 실행 후 서버 재실행
        # sudo pip3 install git+https://github.com/python-visualization/branca.git@master
        text = "<b>"+result[0]['building_name']+"</b></br><i>"+result[0]['city_name']+"</i></br>"

        popText = folium.Html(text+str(lat_long), script=True)
        popup = folium.Popup(popText, max_width=2650)
        folium.Marker(location=lat_long, popup=popup).add_to(m)
        m=m._repr_html_() #updated

        context = {'data':result, 'bldg_map': m}

    return render(request, 'buildings/bldg_detail.html', context)


