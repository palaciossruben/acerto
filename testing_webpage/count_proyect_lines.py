import os


def file_len(fname):
    i = 0
    with open(fname, 'r', errors='replace') as f:
        for _ in f:
            i += 1

    print('{}: {}'.format(fname, i))
    return i


def count_lines(my_path):
    count = 0
    content = os.listdir(my_path)
    #print(content)

    for c in content:
        element_path = os.path.join(my_path, c)
        if os.path.isfile(element_path) and (c.endswith('.py') or c.endswith('.html') or c.endswith('.css') or c.endswith('.js')) and c not in 'bootstrap.min.css' and 'fusioncharts.py' not in c and 'font-awesome.css' not in c and 'slick' not in c and 'animate.css' not in c and 'style' not in c and 'dropzone.js' not in c and 'widgets.css' not in c and 'jquery_easing_plugin' not in c:
            count += file_len(element_path)
        elif os.path.isdir(element_path) and 'GeoLite' not in c and 'fusioncharts' not in c and 'migrations' not in c and 'font-awesome' not in c and 'resumes' not in c and 'CACHE' not in c and 'admin' not in c:
            count += count_lines(element_path)

    return count


print(count_lines('.'))
