import numpy as np
import pandas as pd
from PIL import Image
from PIL import ImageDraw


def draw_image(x_min, coords, text, adress):
    x_min_pd = pd.DataFrame(list(x_min), columns=['id', 'x_min'])
    coords_pd = pd.DataFrame(list(coords), columns=['id', 'x', 'y'])
    merged_pd = pd.merge(coords_pd, x_min_pd, on='id')
    merged_pd['x_calculated'] = merged_pd['x'] - merged_pd['x_min']
    merged_pd['x_calculated'] = merged_pd['x_calculated'] - merged_pd['x_calculated'].min()
    pixels_pd = merged_pd[['x_calculated', 'y']]

    pixels_np = pixels_pd.to_numpy()
    pixels_max = np.max(pixels_np, axis=0)

    image_width = int(pixels_max[0] + 70)
    image_heigth = int(pixels_max[1] + 80)
    image = Image.new('RGB', (image_width, image_heigth), color='white')

    color = (0, 0, 0)

    I1 = ImageDraw.Draw(image)
    I1.text((20, (image_heigth - 70)),
            text,
            fill=(70, 70, 70))

    # braizoma profiliu grupes iliustracija
    for pixel in pixels_np:
        x, y = int(pixel[0] + 40), int(pixel[1])
        image.putpixel((x, y), color)

    # braizoma mastelio liniuote, kas 1 cm
    for y in range(0, image_heigth):
        image.putpixel((0, y), color)

    for y in range(0, image_heigth, 50):
        for x in range(0, 10):
            image.putpixel((x, y), color)

    image.save(adress)

def draw_two_correlated_finds_image(coords, x_min, correlation_queryset):
    text = f'''radiniu id: {correlation_queryset[0]['find_1']}, {correlation_queryset[0]['find_2']}
koreliacija: {correlation_queryset[0]['correlation_x']}
koreliacijos id: {correlation_queryset[0]['id']}
'''
    adress = f'F:/buitine_keramika_tyrimai/tyrimai/Subaciaus_11/grupiu_breziniai_coreliacija/{correlation_queryset[0]["id"]}_id__{correlation_queryset[0]["find_1"]}_{correlation_queryset[0]["find_2"]}_obj.png'
    draw_image(x_min, coords, text, adress)

def draw_group_image(group, coords, x_min):
    text = f'''grupes nr. {group.id},
koreliacija: {group.correlation_x},
tikslumas: {group.precision},
radiniu kiekis: {group.findings_count}'''
    adress = f'F:/buitine_keramika_tyrimai/tyrimai/Subaciaus_11/grupiu_breziniai_coreliacija/{group.id}_gr.png'
    draw_image(x_min, coords, text, adress)


def draw_one_object_group_image(find_id, finds_amount, correlation_x, coords, x_min):
    text = f'''radinio ID. {find_id},
koreliacija: {correlation_x},
radiniu kiekis: {finds_amount}'''
    adress = f'F:/buitine_keramika_tyrimai/tyrimai/Subaciaus_11/grupiu_breziniai_coreliacija/{find_id}_obj_{correlation_x}_corr.png'
    draw_image(x_min, coords, text, adress)
