# gcp-monitor

这个仓库主要是存放GCP监控的脚本。基本的流程如下图：
![image](https://user-images.githubusercontent.com/95392635/185087278-92067db5-9199-4bca-a255-0e7e458396fb.png)


要让functions跑起来其实还是有蛮多需要配置的。

## 配置服务账号
由于代码是通过谷歌的库是获取实例信息。所以我们需要创建一个服务账号作为认证。在创建functions的时候，选择我们创建的服务账号即可。主要的是权限一定要给够。不然会报错

## 创建pub/sub
通过console页面根据提示创建即可，不需要特殊的配置。

