# ImagesMover是什么
批量下载，打包和推送docker镜像的python小工具

# 为什么要写这个工具
在使用docker的过程中，我们经常需要下载一些镜像，然后打包成tar包，然后推送到私有仓库中，这个过程是比较繁琐的，所以写了这个工具来简化这个过程。
  对于网络环境不好的情况下，下载镜像的过程可能会很慢，所以这个工具也可以用来加快镜像移动的步骤。
  对于没有外网访问的环境，可以先在有外网的环境中下载好镜像，然后打包成tar包，然后推送到私有仓库中。

# 使用方法
## 下载,打包镜像
运行完成如下命令后，打包的镜像保存在当前目录的image.tar.gz中
```
python3 images_mover.py --pull-save
```
## 推送镜像
会默认在当前目录下寻找image.tar.gz文件，需要将上一步的打包文件image.tar.gz文件放在当前目录下。执行如下命令后，会将image.tar.gz文件中的镜像推送到私有仓库中
```
python3 images_mover.py --tag-push
```
## 下载,打包,推送镜像
本机作为中转站，下载镜像，打包，推送到私有仓库中。中间不需要保存打包文件，传输文件。
```
python3 images_mover.py --pull -tag-push
```
## 镜像列表和私有仓库
镜像列表和私有仓库的配置在images_mover.py文件image_list和registry_url中，可以根据自己的需要进行修改。

## 说明
代码主要由cursor输出，感谢AI助手协助。