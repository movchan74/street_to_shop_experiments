def get_item_info(product, sess, proxy, cookies):
    item_url = product['url']
    item_id = item_url.split('?')[0].split('/')[-1].split('.html')[0]

    r = sess.get(item_url+'&isOrigTitle=true', cookies=cookies, proxies=proxy, timeout=5.)
    item_soup = bs4.BeautifulSoup(r.text, 'lxml')
    title = item_soup.select_one('h1.product-name').text
    price = item_soup.select_one('span#j-sku-price').text

    try:
        price_disc = item_soup.select_one('span#j-sku-discount-price').text
    except:
        price_disc = None

    rating = float(item_soup.find(itemprop='ratingValue').text)
    review_num = int(item_soup.find(itemprop='reviewCount').text)
    order_num = int(''.join([x for x in item_soup.select_one('span#j-order-num').text if x.isdigit()]))

    props = {}
    for prop in item_soup.select('li.property-item'):
        props[prop.select_one('span.propery-title').text[:-1]] = prop.select_one('span.propery-des').text

    colors = []
    for prop in item_soup.select('dl.p-property-item'):
        if prop.select_one('dt.p-item-title').text == 'Color:':
            for color_item in prop.select('li'):                
                if color_item.select_one('img') is None:
                    color_url = ''
                else:
                    color_url = color_item.select_one('img').attrs['bigpic']
                colors.append({'color': color_item.select_one('a').attrs['title'],
                              'url': color_url})

        if prop.select_one('dt.p-item-title').text == 'Size:':
            sizes = [x.text for x in prop.select('li')]

    images = []
    for image_item in item_soup.select('span.img-thumb-item'):
        images.append(image_item.select_one('img').attrs['src'].replace('_50x50.jpg', '.jpg'))

    store = item_soup.select_one('a.store-lnk').text

    r = sess.get('http:'+item_soup.text.split('window.runParams.descUrl="')[-1].split('"')[0], cookies=cookies, proxies=proxy, timeout=5.)
    desc_soup = bs4.BeautifulSoup(r.text, 'lxml')
    desc_images = [x.attrs['src'] for x in desc_soup.select('img') if 'src' in x.attrs]
    feedback_url = 'http:'+item_soup.select_one('div#feedback').select_one('iframe').attrs['thesrc']

    feedbacks = []
    page = 1
    while True:
        r = sess.get(feedback_url+'&page=%d&withPictures=true'%page, cookies=cookies, proxies=proxy, timeout=10.)
        page += 1
        feedback_soup = bs4.BeautifulSoup(r.text, 'lxml')
        if len(feedback_soup.select('div.feedback-item')) == 0:
            break

        for feedback_item in feedback_soup.select('div.feedback-item'):
            user_country = feedback_item.select_one('div.user-country').text
            feedback_rating = int(feedback_item.select_one('span.star-view').select_one('span').attrs['style'].split('width:')[-1].split('%')[0])

            feedback_props_tmp = []
            for x in feedback_item.select_one('div.user-order-info').text.split('\n'):
                if x.strip() != '':
                    feedback_props_tmp.append(x.strip().replace(' ', ''))

            feedback_props = {}
            for i, x in enumerate(feedback_props_tmp):
                if i%2 == 0:
                    prop_name = x[:-1]
                else:
                    feedback_props[prop_name] = x
 
            try:
                feedback_assignment = feedback_item.select_one('span.product-feedback-info').text.strip()
            except:
                feedback_assignment = None

            personal_info = {}
            for personal_item in feedback_item.select('span.buyer-personal-info-item'):
                personal_item_title = personal_item.select_one('span.buyer-personal-info-title').text[:-1]
                personal_item_value = ''.join(personal_item.findAll(text=True, recursive=False)).strip()
                personal_info[personal_item_title] = personal_item_value

            feedback_images = [x.attrs['data-src'] for x in feedback_item.select('li.pic-view-item')]
            feedback_text = feedback_item.select_one('dt.buyer-feedback').text.strip()
            feedback_time = feedback_item.select_one('dd.r-time').text.strip()

            feedbacks.append({
                'country': user_country,
                'rating': feedback_rating,
                'props': feedback_props,
                'assign': feedback_assignment,
                'person': personal_info,
                'imgs': feedback_images,
                'txt': feedback_text,
                'time': feedback_time,
            })

    item_info = {
        'url': item_url,
        'id': item_id,
        'title': title,
        'price': price,
        'price_disc': price_disc,
        'rating': rating,
        'review_num': review_num,
        'order_num': order_num,
        'props': props,
        'colors': colors,
        'images': images,
        'store': store,
        'desc_images': desc_images,
        'feedbacks': feedbacks,
        'cat': product['cat'],
        'subcat': product['subcat'],
    }

    return item_info