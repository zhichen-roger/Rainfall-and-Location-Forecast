import pandas as pd
from sklearn.cluster import KMeans
import numpy as np
from sklearn.preprocessing import MinMaxScaler


# 将上述数据放到 excel 里，并用 pandas 读取
df = pd.read_excel(r'D:\pythonProjectWeather\weather\test.xlsx', index_col=0)

scale_values =  MinMaxScaler().fit_transform(df.values)  # 数据预处理

kmeans = KMeans(n_clusters=4).fit(scale_values) # 分为 4 类
print(kmeans.labels_) # 输出判别结果列表

# 具体输出判别结果
cluster_1 = []
cluster_2 = []
cluster_3 = []
cluster_4 = []
for i, j in enumerate(kmeans.labels_):
    if j == 0:
        cluster_1.append(df.index[i])
    elif j == 1:
        cluster_2.append(df.index[i])
    elif j==2:
        cluster_3.append(df.index[i])
    else:
        cluster_4.append(df.index[i])
print('类别1')
print(cluster_1)
print('类别2')
print(cluster_2)
print('类别3')
print(cluster_3)
print('类别4')
print(cluster_4)

# draw pictures by tsne, or pca, 利用主成分降维，并画图显示分类结果

#from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
#from mpl_toolkits.mplot3d import Axes3D

tsne = PCA(n_components = 2).fit_transform(scale_values)
df2 = pd.DataFrame(tsne)
df2['labels'] = kmeans.labels_

df_1 = df2[df2['labels'] == 0]
df_2 = df2[df2['labels'] == 1]
df_3 = df2[df2['labels'] == 2]
df_4 = df2[df2['labels'] == 3]
# 画图
plt.figure()
plt.plot(df_1[0], df_1[1], 'yo', df_2[0], df_2[1], 'g*', df_3[0], df_3[1], 'rD',df_4[0], df_4[1], 'bD')
plt.savefig('a.jpg',dpi = 300)
plt.show()
