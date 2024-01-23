# -*- coding: utf-8 -*-
"""11_010_Кулакова_5.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ceEL1f5fvzPXykObxjF-V3CmsuP7mtE0

# Задание на регрессию. Немного о переобучении и недобучении. Кроссвалидация. Подбор параметров.

# Полезные ссылки
* [Переобучение и недобучение](https://neerc.ifmo.ru/wiki/index.php?title=%D0%9F%D0%B5%D1%80%D0%B5%D0%BE%D0%B1%D1%83%D1%87%D0%B5%D0%BD%D0%B8%D0%B5)
* [Регуляризация](https://neerc.ifmo.ru/wiki/index.php?title=%D0%A0%D0%B5%D0%B3%D1%83%D0%BB%D1%8F%D1%80%D0%B8%D0%B7%D0%B0%D1%86%D0%B8%D1%8F)
* [Линейные модели в sklearn - там же есть Лассо и Ридж регрессия](https://scikit-learn.ru/1-1-linear-models/#ridge-regression-and-classification)
* [Выбор и оценка модели](https://scikit-learn.ru/category/model-selection/)
* [Также про регуляризацию, переобучение и недообучение](https://habr.com/ru/companies/ods/articles/323890/)
* [LASSO и Ridge Регрессия. Что же значит та картинка](https://habr.com/ru/articles/679232/)
* [Кроссвалидация](https://academy.yandex.ru/handbook/ml/article/kross-validaciya)
* [Подбор гиперпараметров](https://academy.yandex.ru/handbook/ml/article/podbor-giperparametrov)
* [Статья Себастьяна Рашка](https://arxiv.org/pdf/1811.12808.pdf)
* [Глава 5. Оценка и улучшение качества модели_стр. 268-295](https://disk.yandex.ru/i/XBzXk58TEP349g)

# Переобучение и недобучение

![image.png](attachment:1d398618-1cae-43ac-8aa8-74174afbb9d9.png)

![image.png](attachment:f3bd3fe0-fd01-4ad7-801e-7cb559b68059.png)

# Кроссвалидация
![image.png](attachment:95b905cf-4530-438e-b888-e007b5ade003.png)
"""

# Commented out IPython magic to ensure Python compatibility.
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score, cross_val_predict, cross_validate

from sklearn.linear_model import LinearRegression, Ridge, Lasso, LassoCV, ElasticNet, ElasticNetCV # Линейна регрессия, Ридж и Лассо
from sklearn.linear_model import LassoCV, RidgeCV, MultiTaskLassoCV # Ridge и Lasso Регрессия
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.multioutput import MultiOutputRegressor
# from sklearn.ensemble import GradientBoostingRegressor

from sklearn.metrics import make_scorer, r2_score

from sklearn.pipeline import Pipeline
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import GridSearchCV

import gc

sns.set()
# %matplotlib inline

import sys
# np.set_printoptions(suppress=True)
# np.set_printoptions(threshold=sys.maxsize)
np.set_printoptions(precision=3)

DISPLAY_MAX_ROWS = 20 #20
pd.set_option('display.max_rows', DISPLAY_MAX_ROWS)
pd.set_option('display.max_column',None)
plt.style.use('seaborn-whitegrid')


# plt.rcParams["figure.figsize"] = (20, 15)

import warnings
warnings.filterwarnings('ignore')

# загрузка данных
from google.colab import drive

path = '/content/drive/My Drive/ML/data.csv'
drive.mount('/content/drive')
df = pd.read_csv(path)

df

inputs = ['KS4_GPA5_Qtg.PV', 'KS4_GPA5_TC_T1.PV', 'KS4_GPA5_Nst.PV'] # предикторы
outputs = ['KS4_GPA5_Nvd.PV', 'KS4_GPA5_Nnd.PV', 'KS4_GPA5_T4.PV', 'KS4_GPA5_Pk.PV'] # отклики, целевые признаки

"""# Задача - построить предсказательую модель outputs по inputs
### Результатом решения задачи является код эксперимента в Jupyter Notebook, содержащий качественное обоснование выбора той или иной архитектуры (метода). В качестве base line рекомендуется выбрать модель линейной регрессии.

# ДЗ:
1. Сделать разведочный анализ данных, найти пропуски и выбросы. Примеры есть в ноутбуке EDA_AUTO из 4 задания.
2. Заполнить пропуски. Заполнить медианой или обучить линейную регрессию и заполнить ею пропуски. Если заполните линейной регрессией пропуски, то с помощью таблицы корреляций найдите второй признак, который имеет сильную взаимосвязь с первым признаком. Создаете отдельный датафрейм из этих признаков, исключаете пропуски (не удаляете), обучаете линейну регрессию. Затем прогнозируете на исключенных данных с пропусками и заполняете эти пропуски предсказанным значением.
3. Обучить множественную линейную регрессию. Она будет являться base line, т.е. базовая модель. С ней вы будете сравнивать другие модели.
4. Используя кроссвалидацию, подбор гиперпараметров обучить модели Lasso regression, Ridge Regression, ElasticNet (модель где Ridge + Lasso вместе используется), DecisionTreeRegressor, SVR, RandomForestRegressor

5. `alphas=[0.0001, 0.001,0.01, 0.1, 1, 10]` - для MultiTaskLassoCV, RidgeCV, и для ElasticNetCV.

`'l1_ratio':[0.01, 0.1, 0.5, 1, 5, 10, 15, 20]` - для ElasticNetCV

6. **для SVR и RandomForest:**
```python
param_grid = [{'regressor':[SVR()], 'preprocessing':[StandardScaler(), None],
              'regressor__gamma':[0.001, 0.01, 0.1, 1, 10, 100],
               'regressor__C': [0.001, 0.01, 0.1, 1, 10, 100]},
              {'regressor': [DecisionTreeRegressor()],
               'preprocessing': [None],
               'regressor__max_features': [1, 2, 3]},
              {'regressor': [RandomForestRegressor(n_estimators=100)],
               'preprocessing': [None],
               'regressor__max_features': [1, 2, 3]}]
```

7. **Если SVR обучается, то используем только этот набор параметров:**
```python
param_grid={
    'estimator__gamma': [0.001, 0.01],
    'estimator__C': [0.001, 0.01],
}
```
"""

# Commented out IPython magic to ensure Python compatibility.
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.neighbors import LocalOutlierFactor


import gc

sns.set()
# %matplotlib inline

import sys
np.set_printoptions(suppress=True)
np.set_printoptions(threshold=sys.maxsize)
np.set_printoptions(precision=3)

DISPLAY_MAX_ROWS = 100 #20
pd.set_option('display.max_rows', DISPLAY_MAX_ROWS)
pd.set_option('display.max_column', 100) # None)
plt.style.use('seaborn-whitegrid')


# plt.rcParams["figure.figsize"] = (20, 15)

import warnings
warnings.filterwarnings('ignore')

# пропущенные значения NaN
print(df.isnull().any())
print(df.isna().any())
print(df.isnull().sum())
print(df.isna().sum())
# Заполним медианой
df.fillna(df.median(), inplace=True)
print(df.isnull().sum()) # проверка на пропуски

# Статистический метод (метод межквартильного размаха) - функция для поиска outliers
def find_outliers_IQR(df):
    q1=df.quantile(0.25)
    q3=df.quantile(0.75)
    IQR=q3-q1
    outliers = df[((df<(q1-1.5*IQR)) | (df>(q3+1.5*IQR)))]
    return outliers
df_outliers = find_outliers_IQR(df)
df_outliers[df_outliers.notnull().any(1)]

df_outliers.notnull().sum()

print(df['KS4_GPA5_Pk.PV'].max())
print(df['KS4_GPA5_Pk.PV'].idxmax())
df['KS4_GPA5_Pk.PV'] = df['KS4_GPA5_Pk.PV'].replace(df['KS4_GPA5_Pk.PV'].max(), np.nanmedian(df['KS4_GPA5_Pk.PV']))

X, y = df[inputs], df[outputs]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 0)
regressor = LinearRegression()
regressor.fit(X_train, y_train)
print(regressor.score(X_train, y_train), regressor.score(X_test, y_test))

lasso_regressor = MultiTaskLassoCV(cv = 5, random_state=0, alphas=[0.0001, 0.001,0.01, 0.1, 1, 10])
lasso_regressor.fit(X_train, y_train)
print(lasso_regressor.score(X_train, y_train), lasso_regressor.score(X_test, y_test))

ridge_regressor = RidgeCV(alphas=[0.0001, 0.001,0.01, 0.1, 1, 10])
ridge_regressor.fit(X_train, y_train)
print(ridge_regressor.score(X_train, y_train), ridge_regressor.score(X_test, y_test))

params = {'alpha': [0.0001, 0.001,0.01, 0.1, 1, 10], 'l1_ratio': [0.01, 0.1, 0.5, 1, 5, 10, 15, 20]}
eNet = ElasticNet(max_iter=10000)
grid_search = GridSearchCV(eNet, params)
grid_search.fit(X_train, y_train)
print(grid_search.score(X_train, y_train), grid_search.score(X_test, y_test))

dt_regressor = DecisionTreeRegressor(random_state = 0)
dt_regressor.fit(X_train, y_train)
print(dt_regressor.score(X_train, y_train), dt_regressor.score(X_test, y_test))

param_grid={
 'estimator__gamma': [0.001, 0.01],
 'estimator__C': [0.001, 0.01],
}
grid_search = GridSearchCV(MultiOutputRegressor(SVR()), param_grid=param_grid)
grid_search.fit(X_train, y_train)
print(dt_regressor.score(X_train, y_train), dt_regressor.score(X_test, y_test))

regressor_rf = RandomForestRegressor(n_estimators=100)
params = {'max_features': [1, 2, 3]}
grid_search = GridSearchCV(regressor_rf, params, n_jobs = -1)
grid_search.fit(X_train, y_train)
print(dt_regressor.score(X_train, y_train), dt_regressor.score(X_test, y_test))