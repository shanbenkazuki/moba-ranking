import sqlite3

from copy_text import get_equipment_list_1, get_equipment_list_2, get_equipment_list_3

def get_image_urls(equipment_list, cursor):
    image_urls = []
    for equipment in equipment_list:
        cursor.execute('SELECT image_url FROM mlbb_equipments WHERE name_ja = ?', (equipment,))
        result = cursor.fetchone()
        if result:
            image_urls.append(result[0])
        else:
            print(f"No image_url found for equipment: {equipment}")
            image_urls.append('')
    return image_urls

def create_html(image_urls):
    html_template = """
    <!-- wp:table {{"className":"is-style-regular is-all-centered"}} -->
    <figure class="wp-block-table is-style-regular is-all-centered"><table><tbody><tr><td>
    {}
    </td></tr></tbody></table></figure>
    <!-- /wp:table -->
    """
    images_html = ' '.join([f'<img class="wp-image-XXXX" style="width: 50px;" src="{url}" alt="">' for url in image_urls])
    return html_template.format(images_html)

conn = sqlite3.connect('moba_database.sqlite3')
c = conn.cursor()

equipments_list1  = get_equipment_list_1()
equipments_list2 = get_equipment_list_2()
equipments_list3 = get_equipment_list_3()

for equipments in [equipments_list1, equipments_list2, equipments_list3]:
    image_urls = get_image_urls(equipments, c)
    formatted_html = create_html(image_urls)
    print(formatted_html)

conn.close()
