
## python 版本需要是3.8.x

```
conda install python=3.8
```

## pip 设置私服地址

```
pip config set global.index-url https://nexus.cqliving.com/repository/pypi-group/simple
```

## 安装依赖
```
pip install -r requirements.txt
```

2.提示依赖问题

- kantts

```
pip install kantts -f https://modelscope.oss-cn-beijing.aliyuncs.com/releases/repo.html
```

- ttsfrd

```
pip install ttsfrd -f https://modelscope.oss-cn-beijing.aliyuncs.com/releases/repo.html
```
