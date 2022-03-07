import pandas as pd
import matplotlib.pyplot as plot
from matplotlib.animation import FFMpegWriter, FuncAnimation
import matplotlib
import numpy as np
import scipy
import numpy
import pandas
from tkinter import ttk
import tkinter as tk
from tkinter import filedialog
from tkinter import *
import tkinter
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from functools import partial
import math
from sympy import S, symbols, printing
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib import gridspec
import tkinter.font as font


root = tk.Tk()
style = ttk.Style(root)

# tell tcl where to find the awthemes packages
root.tk.eval("""
set base_theme_dir awthemes-10.4.0

package ifneeded awthemes 10.4.0 \
    [list source [file join $base_theme_dir awthemes.tcl]]
package ifneeded awdark 7.12 \
    [list source [file join $base_theme_dir awdark.tcl]]
""")

root.tk.call("package", "require", 'awdark')
root.tk.call("package", "require", 'awlight')
style.theme_use('awdark')
style.configure('my.TMenubutton', font=('Arial', 15))
style.configure('my.TButton', font=('Arial', 15))
labels_font = font.Font(size=15)


fig = plot.figure(figsize=(10, 6))

browse_secondaryGraph_control_frame = LabelFrame(
    root, width=300, height=300, background="#33393B")
browse_secondaryGraph_control_frame.grid(row=0, column=0, sticky="new")
Grid.rowconfigure(root, 1, weight=1)
Grid.columnconfigure(root, 0, weight=1)

interpolation_graph = LabelFrame(
    root, width=300, height=300, background="#33393B")
interpolation_graph.grid(row=1, column=0, sticky="nsew", columnspan=3)
Grid.rowconfigure(root, 1, weight=1)
Grid.columnconfigure(root, 0, weight=1)

# option_menu_frame=LabelFrame(root, width=300,height=300, background="#33393B")
# option_menu_frame.grid(row=2, column=0, sticky="new")
# Grid.rowconfigure(root, 2, weight=1)
# Grid.columnconfigure(root, 0, weight=1)

interpolation_control_frame = LabelFrame(
    root, width=300, height=300, background="#33393B")
interpolation_control_frame.grid(row=2, column=0, sticky="nsew")
Grid.rowconfigure(root, 2, weight=1)
Grid.columnconfigure(root, 0, weight=1)

errormap_control_frame = LabelFrame(
    root, width=300, height=300, background="#33393B")
errormap_control_frame.grid(row=2, column=2, sticky="nsew")
Grid.rowconfigure(root, 2, weight=1)
Grid.columnconfigure(root, 2, weight=1)

root.configure(bg=style.lookup('TFrame', 'background'))

gridspec_two_graphs = gridspec.GridSpec(2, 1, height_ratios=[5, 5])
gridspec_one_graph = gridspec.GridSpec(1, 1, height_ratios=[5])


interpolation_axis = fig.add_subplot(gridspec_two_graphs[0])
errormap_axis = fig.add_subplot(
    gridspec_two_graphs[1])

# interpolation_axis.set_position(gridspec_one_graph[0].get_position(fig))

visible = True
# errormap_axis.set_visible(visible)


def toggle_errormap_axis():
    global visible
    visible = not visible
    errormap_axis.set_visible(visible)
    if visible:
        interpolation_axis.set_position(
            gridspec_two_graphs[0].get_position(fig))
        errormap_axis.set_position(gridspec_two_graphs[1].get_position(fig))

    else:
        interpolation_axis.set_position(
            gridspec_one_graph[0].get_position(fig))
    plot.draw()


average_error = IntVar()


def browse():
    global data
    global x_axis
    interpolation_axis.cla()
    file_path = filedialog.askopenfilename()
    data = pd.read_csv(file_path)
    x_axis = np.linspace(1, 50, len(data))
    interpolation_axis.plot(x_axis, data['y'])
    interpolation_axis.set_ylabel("amplitude")
    interpolation_axis.set_xlabel("time")
    interpolation_canvas.draw_idle()


eq_latex = 0
equation_list = ["select chunk ploynomial"]
chunk_number_list = ["select chunk ploynomial"]


def option_menu_updater():
    chunks_number_menu['menu'].delete(0, "end")
    for item in chunk_number_list:
        chunks_number_menu['menu'].add_command(
            label=item,
            command=lambda value=item: value_inside.set(value)
        )


value_inside = tkinter.StringVar(root)
value_inside.set(equation_list[0])

x_axis_options = ['Chunks number', 'Degree', 'Overlap']
y_axis_options = ['Degree', 'Chunks number', 'Overlap']

X_axis_value = tkinter.StringVar(root)
X_axis_value.set(x_axis_options[0])

y_axis_value = tkinter.StringVar(root)
y_axis_value.set(y_axis_options[0])


def plotting(x_axis, y_axis, shape):
    interpolation_axis.plot(x_axis, y_axis, shape)
    interpolation_canvas.draw_idle()


def get_latex():
    global chunksnumber
    global fit
    y = symbols("y")
    power = -1
    poly = sum(S("{:6.2f}".format(v))*y**power for power,
               v in enumerate(fit[::-1]-power))
    latex_equation = printing.latex(poly)
    if(chunksnumber == 1):
        fig.text(.5, 0.96, "fitting equation:", ha='center')
        fig.text(.5, 0.92, "${}$".format(latex_equation), ha='center')
        interpolation_canvas.draw_idle()

    return latex_equation


def fitting(x_chunk, y_chunk, polynomial_degree, number_of_chunks):
    global fit
    global extrapolation_Percent

    fit, fitting_error, _, _, _ = np.polyfit(
        x_chunk, y_chunk, polynomial_degree, full=True)
    y_axis = np.poly1d(fit)
    if(number_of_chunks == 1):
        average_error = np.sqrt(fitting_error)
        total_average_error.configure(text=average_error)
        if extrapolation_Percent != 100:
            return fit
        else:
            return y_axis
    else:
        return fitting_error, y_axis


def get_error(error_list, number_of_chunks):
    constant_parameter = []
    actual_error = np.sqrt(error_list)
    for element in actual_error:
        sum1 = 0
        sum1 = sum1 + element
        chunks_average_error = sum1 / number_of_chunks

        if not chunks_average_error:
            chunks_average_error = 0

        constant_parameter = np.append(
            constant_parameter, chunks_average_error)
    return chunks_average_error, constant_parameter


def draw(event):
    global data
    global fit
    global chunkSize
    global average_error
    global extrapolation_Percent

    interpolation_axis.cla()
    interpolation_axis.set_ylabel("amplitude")
    interpolation_axis.set_xlabel("time")
    global chunksnumber
    chunksnumber = entry_Chunk.get()
    print(chunksnumber)
    chunksnumber = int(chunksnumber)
    chunkSize = int(len(x_axis)/chunksnumber)
    polynomial_degree = entry_Degree.get()
    polynomial_degree = int(polynomial_degree)
    extrapolation_Percent = entry_extrapolation.get()
    extrapolation_Percent = int(extrapolation_Percent)
    for text in fig.texts:
        text.set_visible(False)

    if chunksnumber == 1 and extrapolation_Percent == 100:
        plotting(x_axis, data['y'], '-')
        fitting(x_axis, data['y'], polynomial_degree, chunksnumber)
        plotting(x_axis, fitting(
            x_axis, data['y'], polynomial_degree, chunksnumber)(x_axis), '--')
        get_latex()

    elif chunksnumber == 1 and extrapolation_Percent != 100:
        plotting(x_axis, data['y'], '-')
        interpolated_range = int((extrapolation_Percent/100)*len(x_axis))
        intrapolatedx = []
        intrapolatedy = []
        extrapolatedy = []
        for i in range(interpolated_range):
            intrapolatedx.append(x_axis[i])
            intrapolatedy.append(data['y'][i])
        fitting(intrapolatedx, intrapolatedy, polynomial_degree, chunksnumber)
        get_latex()
        for i in range(len(x_axis)):
            extrapolatedy.append(numpy.polyval(fit, x_axis[i]))
        plotting(x_axis, extrapolatedy, '--')

    elif (chunksnumber > 1):
        chunk_number_list.clear()
        equation_list.clear()
        error4 = []
        plotting(x_axis, data['y'], '-')
        chunksy = []
        chunks_length = len(data) / chunksnumber
        overlap_percentage = 100 / chunks_length
        chunksy = overlapped_Chunks(
            data['y'], chunksnumber, overlap_percentage)
        chunksx = overlapped_Chunks(x_axis, chunksnumber, overlap_percentage)
        for i in range(chunksnumber):
            fitting_error, model2 = fitting(
                chunksx[i], chunksy[i], polynomial_degree, chunksnumber)
            error4.append(fitting_error)
            equation_list.append(get_latex())
            chunk_number_list.append(str(i+1))
            option_menu_updater()
            plotting(chunksx[i], model2(chunksx[i]), '--')

        avg_error, average_error_list = get_error(error4, chunksnumber)
        average_error = avg_error
        total_average_error.configure(text=average_error)


error = []
error_list = []



def toggle_error_map_axes(xvariable, yvariable):
    current_const=const
    xcurrent_value = X_axis_value.get()
    ycurrent_value = y_axis_value.get()

    if xcurrent_value == 'Chunks number':
        if ycurrent_value == 'Degree':
            chunkNumber = xvariable
            degree = yvariable
            overlap = current_const
        elif ycurrent_value == 'Overlap':
            chunkNumber = xvariable
            degree = current_const
            overlap = yvariable

    elif xcurrent_value == 'Degree':
        if ycurrent_value == 'Chunks number':
            chunkNumber = yvariable
            degree = xvariable
            overlap = current_const
        elif ycurrent_value == 'Overlap':
            chunkNumber = current_const
            degree = xvariable
            overlap = yvariable

    elif xcurrent_value == 'Overlap':
        if ycurrent_value == 'Chunks number':
            chunkNumber = yvariable
            degree = current_const
            overlap = xvariable
        elif ycurrent_value == 'Degree':
            chunkNumber = current_const
            degree = yvariable
            overlap = xvariable

    return chunkNumber, degree, overlap


def errorMap(event):
    global const
    errormap_axis.cla()
    const = int(constant_Entry.get())
    xMax = int(x_Max.get())
    yMax = int(y_Max.get())
    xaxis = []
    yaxis = []
    zaxis = np.array([], dtype=float)
    progress_bar['value'] = 0
    root.update_idletasks()
    for xvariable in range(1, xMax+1):
        xaxis.append(xvariable)
    if visible == False:
        progress_bar['value'] = 0
        root.update_idletasks()
    else:
        for yvariable in range(1, yMax+1):
            progress_bar['value'] += 100/(yMax)
            root.update_idletasks()
            yaxis.append(yvariable)
            for xvariable in range(1, xMax+1):
                j = 0
                chunkNumber, degree, overlap = toggle_error_map_axes(xvariable, yvariable)
                # if xcurrent_value == 'Chunks number':
                #     if ycurrent_value == 'Degree':
                #         chunkNumber = xvariable
                #         degree = yvariable
                #         overlap = const
                #     elif ycurrent_value == 'Overlap':
                #         chunkNumber = xvariable
                #         degree = const
                #         overlap = yvariable

                # elif xcurrent_value == 'Degree':
                #     if ycurrent_value == 'Chunks number':
                #         chunkNumber = yvariable
                #         degree = xvariable
                #         overlap = const
                #     elif ycurrent_value == 'Overlap':
                #         chunkNumber = const
                #         degree = xvariable
                #         overlap = yvariable

                # elif xcurrent_value == 'Overlap':
                #     if ycurrent_value == 'Chunks number':
                #         chunkNumber = yvariable
                #         degree = const
                #         overlap = xvariable
                #     elif ycurrent_value == 'Degree':
                #         chunkNumber = const
                #         degree = yvariable
                #         overlap = xvariable
                chunksy = overlapped_Chunks(data['y'], chunkNumber, overlap)
                chunksx = overlapped_Chunks(x_axis, chunkNumber, overlap)
                while j < len(chunksx):
                    chunks_error = []
                    error_list = []
                    i = 0
                    fit, fitting_error, _, _, _ = np.polyfit(
                        chunksy[j], chunksx[j], degree, full=True)
                    chunks_error.insert(i, fitting_error)
                    j += 1
                    i += 1

                single_average_error,final_error=get_error(chunks_error,chunkNumber)
                zaxis=np.append(zaxis,single_average_error)
        zaxis = np.reshape(zaxis, (-1, xMax))
        show_error_map = errormap_axis.imshow(zaxis,cmap="hot",origin='lower')
        interpolation_canvas.draw_idle()



def overlapped_Chunks(array, number_Of_Chunks, over_lapping):
    chunks = []
    start = 0
    chunkLength = int(len(array)/(number_Of_Chunks -
                      ((over_lapping/100)*(number_Of_Chunks - 1))))
    stepSize = math.ceil(chunkLength*(1-(over_lapping/100)))
    for i in range(number_Of_Chunks):
        chunk = array[start:start+stepSize]
        chunks.append(np.array(chunk))
        start += stepSize
    return chunks

# def extrapolation(event):
#     global extrapolation_Percent
#     extrapolation_Percent = entry_extrapolation.get()
#     extrapolation_Percent=int(extrapolation_Percent)
#     print (extrapolation_Percent)


def print_answers(event):
    for text in fig.texts:
        text.set_visible(False)
    interpolation_canvas.draw_idle()
    chunkOrder = int(value_inside.get())
    fig.text(.5, 0.96, "fitting equation:", ha='center')
    fig.text(.5, 0.92, "${}$".format(equation_list[chunkOrder]), ha='center')

    return None


value_inside.trace_add(
    "write", lambda *_, select=value_inside: print_answers(select))

choosen_xvariable = tk.StringVar()
Grid.rowconfigure(interpolation_control_frame, 1, weight=1)
Grid.columnconfigure(interpolation_control_frame, 0, weight=1)
chunk_Label = ttk.Label(interpolation_control_frame,
                        text="enter number of chunks")
chunk_Label.grid(row=1, column=0, sticky="nsew")

Grid.rowconfigure(interpolation_control_frame, 2, weight=1)
entry_Chunk = ttk.Scale(interpolation_control_frame,
                        orient='horizontal', from_=1, to=100, command=draw)
entry_Chunk.set(10)
# entry_Chunk = Entry (interpolation_control_frame,width=50)
entry_Chunk.grid(row=2, column=0, sticky="nsew")

Grid.rowconfigure(interpolation_control_frame, 3, weight=1)
degree_Label = ttk.Label(interpolation_control_frame,
                         text="enter degree of chunk")
degree_Label.grid(row=3, column=0, sticky="nsew")

Grid.rowconfigure(interpolation_control_frame, 4, weight=1)
entry_Degree = ttk.Scale(interpolation_control_frame,
                         orient='horizontal', from_=0, to=100, command=draw)
entry_Degree.set(10)
# entry_Degree = Entry (interpolation_control_frame,width=50)
entry_Degree.grid(row=4, column=0, sticky="nsew")

# Grid.rowconfigure(interpolation_control_frame, 5, weight=1)
# Draw_button = ttk.Button(master=interpolation_control_frame, text="draw ",command=draw)
# Draw_button.grid(row=5, column=0, sticky="nsew")
Grid.rowconfigure(interpolation_control_frame, 5, weight=1)
extrapolation_Label = ttk.Label(
    interpolation_control_frame, text="enter interpolation percentage")
extrapolation_Label.grid(row=5, column=0, sticky="nsew")

Grid.rowconfigure(interpolation_control_frame, 6, weight=1)

entry_extrapolation = ttk.Scale(
    interpolation_control_frame, orient='horizontal', from_=0, to=100, command=draw)
entry_extrapolation.set(10)
# entry_extrapolation = Entry (interpolation_control_frame,width=50)
entry_extrapolation.grid(row=6, column=0, sticky="nsew")

# Grid.rowconfigure(interpolation_control_frame, 7, weight=1)
# Extrapolation_button = ttk.Button(master=interpolation_control_frame, text="enter interpolation percentage " ,command=extrapolation)
# Extrapolation_button.grid(row=7, column=0, sticky="nsew")

Grid.rowconfigure(interpolation_control_frame, 8, weight=1)
error_Label = ttk.Label(interpolation_control_frame, text="Error is")
error_Label.grid(row=8, column=0, sticky="nsew")

Grid.rowconfigure(interpolation_control_frame, 9, weight=1)
total_average_error = ttk.Label(interpolation_control_frame)
total_average_error.grid(row=9, column=0, sticky="nsew")

Grid.rowconfigure(errormap_control_frame, 1, weight=1)
Grid.columnconfigure(errormap_control_frame, 0, weight=1)
# choosen_xaxis = ttk.Combobox(errormap_control_frame, width=27,
#                              textvariable=choosen_xvariable)

# choosen_xaxis['values'] = ('Chunks number', 'Degree', 'Overlap')
# choosen_xaxis.grid(row=1, column=0, sticky="nsew")
# choosen_xaxis.set('x-axis')

Grid.rowconfigure(errormap_control_frame, 2, weight=1)
# choosen_yvariable = tk.StringVar()
# choosen_yaxis = ttk.Combobox(errormap_control_frame, width=27,
#                              textvariable=choosen_yvariable)

# choosen_yaxis['values'] = ('Chunks number', 'Degree', 'Overlap')
# choosen_yaxis.grid(row=2, column=0, sticky="nsew")
# choosen_yaxis.set('y-axis')

Grid.rowconfigure(errormap_control_frame, 3, weight=1)
constant_Label = ttk.Label(errormap_control_frame, text="constant entry=")
constant_Label.grid(row=3, column=0, sticky="nsew")

Grid.rowconfigure(errormap_control_frame, 4, weight=1)
constant_Entry = ttk.Scale(
    errormap_control_frame, orient='horizontal', from_=0, to=100, command=errorMap)
constant_Entry.set(10)
# constant_Entry = Entry (errormap_control_frame,width=50)
constant_Entry.grid(row=4, column=0, sticky="nsew")

Grid.rowconfigure(errormap_control_frame, 5, weight=1)
xMAxLabel = ttk.Label(errormap_control_frame, text="max value of x_axis=")
xMAxLabel.grid(row=5, column=0, sticky="nsew")

Grid.rowconfigure(errormap_control_frame, 6, weight=1)
# x_Max = Entry (errormap_control_frame,width=50)
x_Max = ttk.Scale(errormap_control_frame, orient='horizontal',
                  from_=0, to=100, command=errorMap)
x_Max.set(10)
x_Max.grid(row=6, column=0, sticky="nsew")

Grid.rowconfigure(errormap_control_frame, 7, weight=1)
yMAxLabel = ttk.Label(errormap_control_frame, text="max value of y_axis=")
yMAxLabel.grid(row=7, column=0, sticky="nsew")

Grid.rowconfigure(errormap_control_frame, 8, weight=1)
# y_Max = Entry (errormap_control_frame,width=50)
y_Max = ttk.Scale(errormap_control_frame, orient='horizontal',
                  from_=0, to=100, command=errorMap)
y_Max.set(10)
y_Max.grid(row=8, column=0, sticky="nsew")

# Grid.rowconfigure(errormap_control_frame, 9, weight=1)
# ErrorMap_button = ttk.Button(master=errormap_control_frame, text="draw error map " ,command=errorMap)
# ErrorMap_button.grid(row=9, column=0, sticky="nsew")

Grid.rowconfigure(errormap_control_frame, 10, weight=1)
progress_bar = ttk.Progressbar(
    errormap_control_frame, orient='horizontal', mode='determinate', length=280)
progress_bar.grid(row=10, column=0, sticky="nsew")

Grid.rowconfigure(browse_secondaryGraph_control_frame, 0, weight=1)
Grid.columnconfigure(browse_secondaryGraph_control_frame, 0, weight=1)
Browse_button = ttk.Button(
    master=browse_secondaryGraph_control_frame, text="browse for signal", command=browse, style='my.TButton')
Browse_button.grid(row=0, column=0, sticky="nsew")

Grid.columnconfigure(browse_secondaryGraph_control_frame, 1, weight=1)
Close_button = ttk.Button(master=browse_secondaryGraph_control_frame, text="open/close secondary graph ",
                          command=toggle_errormap_axis, style='my.TButton')
Close_button.grid(row=0, column=1, sticky="nsew")

Grid.rowconfigure(interpolation_control_frame, 10, weight=1)
chunks_number_menu = ttk.OptionMenu(
    interpolation_control_frame, value_inside, *equation_list, style='my.TMenubutton')
chunks_number_menu.grid(row=10, column=0, sticky="nsew")


X_axis_menu = ttk.OptionMenu(
    errormap_control_frame, X_axis_value, *x_axis_options, style='my.TMenubutton')
X_axis_menu.grid(row=1, column=0, sticky="nsew")

Y_axis_menu = ttk.OptionMenu(
    errormap_control_frame, y_axis_value, *y_axis_options, style='my.TMenubutton')
Y_axis_menu.grid(row=2, column=0, sticky="nsew")

Grid.rowconfigure(interpolation_graph, 0, weight=1)
Grid.columnconfigure(interpolation_graph, 0, weight=1)
# A tk.DrawingArea.
interpolation_canvas = FigureCanvasTkAgg(fig, master=interpolation_graph)
interpolation_canvas.draw()
interpolation_canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
xMAxLabel['font'] = labels_font
yMAxLabel['font'] = labels_font
chunk_Label['font'] = labels_font
degree_Label['font'] = labels_font
extrapolation_Label['font'] = labels_font
error_Label['font'] = labels_font
# choosen_xaxis['font'] = labels_font
# choosen_yaxis['font'] = labels_font
constant_Label['font'] = labels_font

tkinter.mainloop()
