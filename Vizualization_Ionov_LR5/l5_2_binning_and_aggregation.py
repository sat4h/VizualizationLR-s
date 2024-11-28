# -*- coding: utf-8 -*-
"""L5-2-Binning-and-aggregation.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1_D0222nxxVdZC-IEzsM8L5guSfEVmX37

## Группировка данных

Мы изучили **данные (data)**, **метки (marks)**, **кодирования (encodings)** и **типы кодирования (encoding types)**.
Следующая ключевая часть API Altair'а – его подход к группировке данных
"""

import altair as alt

from vega_datasets import data
cars = data.cars()

cars.head()

"""### Group-By в Pandas

Одна из ключевых операций в исследовании данных это *group-by*, подробно разбираемая в [Главе 4](https://jakevdp.github.io/PythonDataScienceHandbook/03.08-aggregation-and-grouping.html) книги *Python Data Science Handbook*.
Если коротко, group-by разделяет данные на группы в соответствии с некоторым условием, применяет некоторую функцию объединения внутри этих групп, а затем объединяет данных обратно:

![Split Apply Combine figure](split-apply-combine.png)
[Оригинал изображения](https://jakevdp.github.io/PythonDataScienceHandbook/03.08-aggregation-and-grouping.html)

Для данных из набора cars, можно сгруппировать данные по признакоу Origin, вычислить среднее значение миль на галлон, а затем объединить результаты.
В Pandas эта операция будет выглядеть следующим образом:
"""

cars.groupby('Origin')['Miles_per_Gallon'].mean()

"""В Altair такая операция разделения-вычисления-объединения может быть выполнена посредством передачи оператора объединения в любую кодировку. Например, график представляющий описанную выше операцию формируется следующим образом:"""

alt.Chart(cars).mark_bar().encode(
    y='Origin',
    x='mean(Miles_per_Gallon)'
)

"""Заметим, что группировка выполняется внутри кодировки неявно: мы группируем по Origin и вычисляем среднее по каждой группе.

### Одномерное накопление (binning): гистограммы

Наиболее распространённым использованием накопления данных является создание гистограмм. Например, визуализируем гистограмму миль за галлон.
"""

alt.Chart(cars).mark_bar().encode(
    alt.X('Miles_per_Gallon', bin=True),
    alt.Y('count()'),
    alt.Color('Origin')
)

"""Интересным свойством декларативного подхода Altair является возможность присвоения этих значений различным кодированиям, позволяющая иначе визуализировать те же данные.

Например, если присвоить накапливаемые мили за галлон цвету, можно получить следующий график:
"""

alt.Chart(cars).mark_bar().encode(
    color=alt.Color('Miles_per_Gallon', bin=True),
    x='count()',
    y='Origin'
)

"""Это позволяет лучше оценить пропорции значений внутри каждой страны.

Если мы хотим, можем нормализовать эти значения по оси x, чтобы напрямую сравнить пропорции:
"""

alt.Chart(cars).mark_bar().encode(
    color=alt.Color('Miles_per_Gallon', bin=True),
    x=alt.X('count()', stack='normalize'),
    y='Origin'
)

"""Как можно увидеть, больше половины автомобилей США относятся к категории высокого расхода топлива..

Снова изменим кодирование. Пусть теперь цвет соответствует количеству:
"""

alt.Chart(cars).mark_rect().encode(
    x=alt.X('Miles_per_Gallon', bin=alt.Bin(maxbins=20)),
    color='count()',
    y='Origin',
)

"""Теперь этот же набор данных представлен в форме тепловой карты.

Altair позволяет ещё и показать связь между различными типами графиков!

### Другие функции группировки

Агрегаторы могут использованы с данными, которые были накоплены неявно. Например, посмотрим на график миль за галлон по времени:
"""

alt.Chart(cars).mark_point().encode(
    x='Year:T',
    color='Origin',
    y='Miles_per_Gallon'
)

"""Тот факт, что точки так сильно перекрывают друг друга, затрудняет чтение важных частей графика.

Можно сделать этот график понятнее, нарисовав среднее значение каждой группы:
"""

alt.Chart(cars).mark_line().encode(
    x='Year:T',
    color='Origin',
    y='mean(Miles_per_Gallon)'
)

"""Среднее показывает только часть информации, но Altair предоставляет инструмент для вычисления нижних и верхних границ доверительных интервалов.

Можно использовать ``mark_area()`` и задать нижнюю и верхнюю границы с использованием ``y`` and ``y2``:
"""

alt.Chart(cars).mark_area(opacity=0.3).encode(
    x='Year:T',
    color='Origin',
    y='ci0(Miles_per_Gallon)',
    y2='ci1(Miles_per_Gallon)'
)

"""## Группировка по времени

Один из специфичных видов объединения – группировка по различным аспектам даты, по месяцу, году или дню.
Посмотрим на простой набор данных погоды в Сиэттле:
"""

temps = data.seattle_temps()
temps.head()

"""Если мы попытаемся визуализировать эти данные, то получим ``MaxRowsError``:"""

# alt.Chart(temps).mark_line().encode(
#     x='date:T',
#     y='temp:Q'
# )

len(temps)

"""### Немного информации: Как Altair интерпретирует данные

Ошибка MaxRowsError для наборов данных больше, чем 5000 возникает, поскольку бездумное использование Altair без понимания, как в нём представляются данные, приводит к **очень** большим jupyter notebook'ам, что сильно влияет на производительность.

Когда датафрейм pandas передаётся в график Altair, все данные конвертируются в JSON и хранятся как спецификация графика. Эта спецификация встраивается в notebook и 20-30 графиков для достаточно большого набора данных приводит к резкому падению производительности.

Как избавиться от ошибки? Есть несколько способов:

1) Использовать меньший набор данных. Например, объединить данные температуры по дням:
   ```python
   import pandas as pd
   temps = temps.groupby(pd.DatetimeIndex(temps.date).date).mean().reset_index()
   ```

2) Отключить MaxRowsError с использованием
   ```python
   alt.data_transformers.enable('default', max_rows=None)
   ```
   Ещё раз, это может привести к *очень* большим блокнотам при отсутствии должного внимания.
   
3) Поместить данные на локальный сервер. Модуль [сервер данных Altair](https://github.com/altair-viz/altair_data_server) упростит процедуру.
   ```python
   alt.data_transformers.enable('data_server')
   ```
   Этот подход может не работать на некоторых облачных сервисах Jupyter notebook.
   
4) Использовать ссылку URL, указывающую на источник данных. Создание [gist](gist.github.com) – быстрый и простой способ хранения часто используемых данных.

Мы попробуем последний способ, поскольку он наиболее универсальный и обеспечивает наилучшую производительность. Для всех наборов данных из `vega_datasets` есть параметр `url`, однако в этой работе мы воспользуемся прямой ссылкой на `vega.github.io`.
"""

temps = 'https://vega.github.io/vega-datasets/data/seattle-weather-hourly-normals.csv'

alt.Chart(temps).mark_line().to_dict()

"""Обратите внимание, что вместо использования всего набора данных используется только url.

Попробуем визуализировать график:
"""

alt.Chart(temps).mark_line().encode(
    x='date:T',
    y='temperature:Q'
)

"""Здесь очень много данных. Объединим их по месяцам:"""

alt.Chart(temps).mark_point().encode(
    x=alt.X('month(date):T'),
    y='temperature:Q'
)

"""График станет понятнее, если объединить данные по температуре (среднее):"""

alt.Chart(temps).mark_bar().encode(
    x=alt.X('month(date):O'),
    y='mean(temperature):Q'
)

"""Также можно разделить даты разными способами для получения интересных визуализаций. Например, средняя температура по дням в течение месяца:"""

alt.Chart(temps).mark_rect().encode(
    x=alt.X('date(date):O'),
    y=alt.Y('month(date):O'),
    color='mean(temperature):Q'
)

"""Или средняя температура по часам в течение месяца:"""

alt.Chart(temps).mark_rect().encode(
    x=alt.X('hours(date):O'),
    y=alt.Y('month(date):O'),
    color='mean(temperature):Q'
)

"""Больше информации по ``TimeUnit Transform`` можно найти здесь: https://altair-viz.github.io/user_guide/transform/timeunit.html#user-guide-timeunit-transform"""