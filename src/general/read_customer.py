import os


def read_customer_from_excel(url):
    from copy import deepcopy
    import xlrd
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    file_location = "{}{}".format(BASE_DIR,url)
    work_book = xlrd.open_workbook(file_location)
    sheet = work_book.sheet_by_index(0)
    nrows = sheet.nrows
    ncols = sheet.ncols
    all_list = []
    for nrows_item in range(nrows):
        result = ""
        if nrows_item > 0:
            name = ""
            address_1 = ""
            address_2 = ""
            post = ""
            address = "{} {} {}"
            work_time = 0
            minute = ""
            latitude = 0
            longitude = 0
            # ncols_i = 0
            for ncols_item in range(ncols):
                if ncols_item == 0:
                    name = sheet.cell_value(nrows_item,ncols_item)
                if ncols_item == 1:
                    address_1 = sheet.cell_value(nrows_item,ncols_item)
                if ncols_item == 2:
                    post = sheet.cell_value(nrows_item,ncols_item)
                if ncols_item == 3:
                    address_2 = sheet.cell_value(nrows_item,ncols_item)
                if ncols_item == 5:
                    work_time = sheet.cell_value(nrows_item,ncols_item)
                result = "{} - {}.{} {}".format(result,nrows_item,ncols_item,sheet.cell_value(nrows_item,ncols_item))
                if ncols_item == 11:
                    minute = sheet.cell_value(nrows_item,ncols_item)
                if ncols_item == 13:
                    latitude = sheet.cell_value(nrows_item,ncols_item)
                if ncols_item == 14:
                    longitude = sheet.cell_value(nrows_item,ncols_item)
                result = "{} - {}.{} {}".format(result,nrows_item,ncols_item,sheet.cell_value(nrows_item,ncols_item))
            all_list.append([deepcopy(name),address.format(deepcopy(address_1),int(float(deepcopy(post))),deepcopy(address_2)).strip(),deepcopy(int(float(work_time))),int(round(float(deepcopy(minute)))),deepcopy(float(latitude)),deepcopy(float(longitude))])
    print("---------------------------------------------------------------")
    print(all_list)
    print(len(all_list))
    print("---------------------------------------------------------------")
    return all_list



