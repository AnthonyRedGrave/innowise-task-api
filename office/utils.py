

def check_date(qs):
    print("проверка даты для бронирования")
    if qs.count() > 0:
        for place in qs:
            if place.release_place():
                print("{} было освобождено!".format(place))
                place.reset_fields()
    return qs