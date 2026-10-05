columns = ["col1", "col2", "col3"]
values = [1, 2, 3]

filter_list = list(zip(columns, values))
print(filter_list)
filter_list = [(x,">", y) for x, y in filter_list]
print(filter_list)