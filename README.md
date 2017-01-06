# simpleSearchEngine
搭建一个简单的引擎服务，几乎包含所有中间工作, 内容选取篮球网站虎扑的湿乎乎论坛
- spider(抓取)
- parser(解析)
- engine(搜索引擎)
- suggest(推荐服务)
- server(搜索接口)

## spider + parser

使用python 写的抓取脚本，parser 使用BeautifulSoup; 建库的数据抓取了有20多万条有效数据，从11年到现在的，抽取了标题、内容、评论等信息, 不过由于阿里云服务器配置较差，最后就只使用了5万条数据。

## engine
使用solr-6.2.0版本，直接编译好的版本。solr的rank方式需要调，所以在搜索接口中支持较多中排序，solr的字段配置以及请求的方式也会在代码和文件中有所体现

## suggest
使用抓取数据的标题(22万条)，结巴分词，去除停用词，训练出的word2vec模型，再使用python搭建web服务，提供相关词suggest服务

## server
搜索接口，使用nginx + phpfpm + html + ajax + css构建搜索窗口，底层调用solr和suggest服务

## 测试接口
http://112.74.45.38/web/summary.html
