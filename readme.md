#### ProxyPool-HTTP代理完整版

```python
# 项目需要部署在vps上，推荐部署在云立方[https://www.yunlifang.cn/dynamicvpsjsxzdx.asp]
```

##### 运行方式

```
nohup python3  run.py >/dev/null 2>&1 &
```

##### 辅助服务

```python
# 0. redis
# 1. tiny proxy
```

##### tiny proxy

```shell
# 安装方法
yum install -y epel-release
yum update -y
yum install -y tinyproxy
# 配置
# 配置文件 /etc/tinyproxy/tinyproxy.conf 
Port 8888
# Allow 127.0.0.1
# 重启TinyProxy
systemctl enable tinyproxy.service
systemctl restart tinyproxy.service
# 开放端口
iptables -I INPUT -p tcp --dport 8888 -j ACCEPT
# 验证
curl -x 112.84.118.216:8888 httpbin.org/get
```

##### 添加API接口

```python
# 部署在redis所在服务器上
# 运行方式 nohup python3 api.py >/dev/null 2>&1 &
```

[目前GitHub进度](https://github.com/squabbysheep/ProxyPool/tree/master)

[API接口](http://121.36.55.134:80)

