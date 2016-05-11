# !/usr/bin/env python
# encoding: utf-8

"""
PopART_Xtreme
SVG-manipulating program
Created by Andre Moncrieff on 4 April 2016.
Modified 24 April 2016.
Copyright 2016 Andre E. Moncrieff, Glaucia C. Del-Rio & Marco A. Rego.
All rights reserved.
"""

import re
import argparse
import pandas
from bokeh.io import output_file, show
from bokeh.models import (GMapPlot, GMapOptions, ColumnDataSource,
                          Circle, DataRange1d, PanTool, WheelZoomTool,
                          BoxSelectTool, BoxZoomTool, PreviewSaveTool,
                          HoverTool)


def parser():
    """
    Argparse function to get the function arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--SVG", required=True,
                        help="input the .svg file from PopArt",
                        type=str)
    parser.add_argument("--LOG", required=True,
                        help="input the .log file from PopArt",
                        type=str)
    parser.add_argument("--TXT", required=True,
                        help="input the .txt file (Tab delimited) with at"
                        " least Lat, Long, Sequence and Locality fields",
                        type=str)
    parser.add_argument("--OUT", required=True,
                        help="input the .html file. "
                        "This will be the final file",
                        type=str)
    args = parser.parse_args()
    return args


def read_in(file):
    """opens SVG file (input from PopART) and transforms it in a list"""
    with open(file, "r") as in_file:
            list_of_lines = []
            for line in in_file:
                list_of_lines.append(line.strip("\n"))
    return list_of_lines


def remove_labels(list_of_lines):
    """removes the labels from the original SVG file, so the complete information is 
    displyed by the tooltip"""
    counter = 0
    no_labels_list = []
    for line in list_of_lines[1:]:
        if "<text " not in line:
            no_labels_list.append(line)
            counter += 1
        else:
            internal_counter = 0
            if internal_counter == 0:
                modified_line = line.replace('fill-opacity="1" ',
                                             'fill-opacity="0" ')
                no_labels_list.append(modified_line)
            counter += 1
    return no_labels_list


def add_tooltip1(some_list_of_lines, my_dict):
    """
    Adds css style and js code for the tooltip to the svg file
    """
    empty_lis = []
    for key, value in my_dict.items():
        empty_lis.append(len(value))
    number_of_lines = max(empty_lis)
    updated_lol = []
    for line in some_list_of_lines:
        line = line.replace("\n", "")
        if 'Profile="tiny"' in line:
            modified_line = line.replace('Profile="tiny"',
                                         'Profile="tiny" onload="init(evt)"')
            updated_lol.append(modified_line)
        if '</defs>' in line:
            updated_lol.append(line)
            updated_lol.append('<style type="text/css">.land{fill: #b9b9b9;'
                               'stroke: white;stroke-width: 1.5;'
                               'stroke-miterlimit: 4;}.coast{stroke-width:'
                               ' 0.5;}.label{font-size: 14px;}.tooltip{font-'
                               'size: 18px; font-family: "Helvetica Neue", '
                               'Helvetica, Arial, sans-serif;}.tooltip_bg{fill'
                               ': white; stroke: black; stroke-width: 1; '
                               'opacity: 1;}</style>')
            updated_lol.append('<script><![CDATA[')
            updated_lol.append('function ShowTooltip(evt, mouseovertext){')
            updated_lol.append('var tooltip = document.getElementById'
                               '("tooltip");')
            updated_lol.append('var tooltip_text = tooltip.'
                               'childNodes.item(1);')
            updated_lol.append("var words = mouseovertext.split('\\n');")
            updated_lol.append('var max_length = 0;')
            updated_lol.append('for (var i=0; i<4; i++){')
            updated_lol.append('tooltip_text.childNodes.item(i).firstChild.'
                               'data = i<words.length ?  words[i] : " ";')
            updated_lol.append('length = tooltip_text.childNodes.item(i).'
                               'getComputedTextLength();')
            updated_lol.append('if (length > max_length) '
                               '{max_length = length;}}')
            updated_lol.append('var x = evt.clientX')
            updated_lol.append('var y = evt.clientY')
            updated_lol.append('tooltip.setAttributeNS(null,"transform", '
                               '"translate(" + x + " " + y + ")")')
            updated_lol.append('tooltip.setAttributeNS(null,'
                               '"visibility","visible");}')
            updated_lol.append('function HideTooltip(evt){')
            updated_lol.append('var tooltip = document.getElementById'
                               '("tooltip");')
            updated_lol.append('tooltip.setAttributeNS(null,"visibility",'
                               '"hidden");}')
            updated_lol.append(']]></script>')
        if '</svg>' in line:
            updated_lol.append("""<g class="tooltip" id="tooltip" visibility"""
                               """"=hidden">""")
            updated_lol.append('<text><tspan> </tspan><tspan x="0" dy="20">'
                               ' </tspan><tspan x="0" dy="20"> </tspan><tspan'
                               ' x="0" dy="20"> </tspan>')
            for n in range(number_of_lines):
                updated_lol.append('<tspan x="0" dy="20"> </tspan><tspan x="0"'
                                   ' dy="20"> </tspan><tspan x="0" dy="20">'
                                   ' </tspan><tspan x="0" dy="20"> </tspan>')
            updated_lol.append('<tspan x="0" dy="20"> </tspan><tspan x="0" '
                               'dy="20"> </tspan><tspan x="0" dy="20"> </tspan'
                               '><tspan x="0" dy="20"> </tspan></text></g>')
            updated_lol.append(line)
        if 'Profile="tiny"' not in line:
            if '</defs>' not in line:
                if '</svg>' not in line:
                    updated_lol.append(line)
    return updated_lol


def information_oppener(tab_del_file):
    """
    opens tab delimited file and transforme it in a list
    """
    with open(tab_del_file, 'r') as dicio:
        lista = []
        list(map(lambda line: lista.append(line.replace('\n', '').split('\t')),
             dicio))
        lista = lista[1:]
    return lista


def log_oppener(log_file):
    """
    opens tab delimited file and transforme it in a list
    """
    with open(log_file, 'r') as dicio:
        lista = []
        list(map(lambda line: lista.append(line.replace('\n', '').split('\t')),
             dicio))
        lista = lista[1:]
    return lista


def fill_cells(lista):
    '''
    This function fills empty cells of a list of lists (spreadsheet) based on
    the information of the cell above. It is just like ctrl+d in excel
    '''
    for val in lista:
        if val[0] == "":
            check = lista.index(val)
            right = lista[check-1]
            if right[0] != '':
                val.insert(0, right[0])
    for item in lista:
        for subitem in item:
            if subitem == '':
                ind = item.index(subitem)
                item.pop(ind)
    return lista


def word_counter(my_list):
    '''
    transforms the previous list (derived from the original log file) in a
     dictionary
    '''
    my_dict = {}
    for word in my_list:
        if word[0] not in my_dict:
            my_dict[word[0]] = [word[1]]
        elif word[0] in my_dict:
            my_dict[word[0]].append(word[1])
    for key, value in my_dict.items():
        my_dict[key] = list(set(value))
    return my_dict


def manipulate_log(dictn, information):
    """
    Deals with the log file dictionary
    """
    for key in dictn.keys():
        for item in information:
            for value in dictn[key]:
                if value == item[0]:
                    ind = dictn[key].index(value)
                    item = ", ".join(item)
                    item = item.replace('"', "")
                    item = item.replace("'", "")
                    dictn[key].append(item)
                    dictn[key].pop(ind)
    return dictn


def add_tooltip2(lines_svg, information, several_seq):
    """
    Adds tooltip elements to specific svg lines, matching the svg original
     labels
    """
    lis = list(range(len(several_seq)))
    for key, values in several_seq.items():
        for num in lis:
            values.insert(0, "Haplotype: " + str(list(several_seq.keys()).index
                          (key)))
            break
        value = "\\n".join(values)
        value = value.replace('"', "")
        value = value.replace("'", "")
        for lista in information:
            if lista[0] in several_seq.keys():
                for line in lines_svg:
                    my_string = re.findall("^ >"+key+"</text>$", line)
                    if my_string != []:
                        var = (lines_svg.index(line))-1
                        previous = lines_svg[var]
                        line0 = previous.replace(">", "")
                        line1 = line0 + " onmousemove="
                        line2 = line1 + """ "ShowTooltip(evt,'""" + value + """')" """
                        line3 = line2 + ' onmouseout="HideTooltip(evt)">'
                        lines_svg.pop(var)
                        lines_svg.insert(var, line3)
                    else:
                        pass
            else:
                info = ",".join(lista)
                info = info.replace('"', "")
                info = info.replace("'", "")
                for line in lines_svg:
                    my_string = re.findall("^ >"+lista[0]+"</text>$", line)
                    if my_string != []:
                        var = (lines_svg.index(line))-1
                        previous = lines_svg[var]
                        line0 = previous.replace(">", "")
                        line1 = line0 + " onmousemove="
                        line2 = line1 + """ "ShowTooltip(evt,'""" + info + """')" """
                        line3 = line2 + ' onmouseout="HideTooltip(evt)">'
                        lines_svg.pop(var)
                        lines_svg.insert(var, line3)
                    else:
                        pass
    return lines_svg, several_seq


def cleaning_svg(lines_svg):
    """
    Uses regex to post-clean the svg, extracting possible extra onmouse actions
    """
    for line in lines_svg:
        my_string = re.findall('onmousemove', line)
        ind = lines_svg.index(line)
        if len(my_string) > 1:
            test = line.split('onmousemove')
            check = 'onmousemove'.join(test[0:2])+'>'
            lines_svg.pop(ind)
            lines_svg.insert(ind, check)
        else:
            pass
    return lines_svg


def viewbox_manager(lista):
    """
    Changes the viewBox parameters in the svg file
    so map, network and tooltips appear in the same html
    """
    svg_header = lista[0]
    view_box_line = lista[1]
    svg_sizes = re.findall("\d+\.\d+", svg_header)
    svg_vb = re.findall("\d+", view_box_line)
    double = [str(float(d)*2) for d in svg_sizes]
    triple = [str(int(n)*3) for n in svg_vb]
    new_header = "<svg width="+'"'+double[0]+'mm" height='+'"'+double[1]+'mm"'
    new_view_box = ' viewBox="0 0 ' + triple[2] + ' ' + triple[3] + '"'
    lista.pop(0)
    lista.pop(0)
    lista.insert(0, new_header)
    lista.insert(1, new_view_box)


def create_map(tab_del_file):
    """
    This function was adapted from bokeh tutorial, so it might have similar
     elements in it.
    """
    data = pandas.read_csv(tab_del_file, sep="\\t", engine='python')
    lat_mean = data["Lat"].mean()
    long_mean = data["Long"].mean()
    map_options = GMapOptions(lat=lat_mean, lng=long_mean, map_type="hybrid",
                              zoom=5)
    plot = GMapPlot(x_range=DataRange1d(),
                    y_range=DataRange1d(),
                    map_options=map_options,
                    title="PopART-XTREME"
                    )
    source = ColumnDataSource(data=dict(lat=[x for x in data["Lat"]],
                                        lon=[y for y in data["Long"]],
                                        name=[s for s in data["Sequence"]],
                                        local=[l for l in data["Locality"]]))
    circle = Circle(x="lon", y="lat", size=15, fill_color="blue",
                    fill_alpha=0.8, line_color=None)
    tooltips = [("Sequence", "@name"), ("Locality", "@local")]

    render = plot.add_glyph(source, circle)
    plot.add_tools(PanTool(), WheelZoomTool(), BoxSelectTool(), BoxZoomTool(),
                   PreviewSaveTool(), HoverTool(tooltips=tooltips,
                   renderers=[render]))
    output_file("map_plot.html")
    show(plot)


def mix_files(mapp, svg):
    """
    This function appends the original svg file (out from PopART)
     to the html representing the map generated by the bokeh function
    """
    body = "</body>"
    html = "</html>"
    newfile_lis = []
    for line in mapp:
        if body in line:
            mapp.pop(mapp.index(line))
        if html in line:
            mapp.pop(mapp.index(line))
    for l in mapp[1:]:
        newfile_lis.append(l)
    for lin in svg:
        newfile_lis.append(lin)
    for l in newfile_lis:
        if "<body>" in l:
            ind_body = newfile_lis.index(l)
            newfile_lis.insert(ind_body+1,
                               '<div position:relative; width="100%"; '
                               'height="400px">')
            newfile_lis.insert(ind_body+2,
                               '<div width="50%" height="400px" '
                               'style="float:left">')
            break
    for li in newfile_lis:
        if "<svg " in li:
            ind_svg = newfile_lis.index(li)
            newfile_lis.insert(ind_svg,
                               '<div width="80%" height="400px" '
                               'style="float:left">')
            newfile_lis.insert(ind_svg, '</div>')
            break
    newfile_lis.append('</div>')
    newfile_lis.append('</div>')
    newfile_lis.append(body)
    newfile_lis.append(html)
    return newfile_lis


def writer(final_list_of_lines, final_file):
    """
    function to write the final html
    """
    with open(final_file, "w") as outfile:
        for line in final_list_of_lines:
            outfile.write(line)
            outfile.write("\n")


def main():
    args = parser()
    list_of_lines = read_in(args.SVG)
    information = information_oppener(args.TXT)
    lista = log_oppener(args.LOG)
    filled = fill_cells(lista)
    log_dicio = word_counter(filled)
    several_seq = manipulate_log(log_dicio, information)
    no_labels_lol = remove_labels(list_of_lines)
    tooltippy_lol1 = add_tooltip1(no_labels_lol, log_dicio)
    tooltippy_lol2, seq_dict = add_tooltip2(tooltippy_lol1, information,
                                            several_seq)
    clean = cleaning_svg(tooltippy_lol2)
    viewbox_manager(clean)
    create_map(args.TXT)
    map_file = read_in("map_plot.html")
    mixed = mix_files(map_file, clean)
    writer(mixed, args.OUT)

if __name__ == '__main__':
    main()
