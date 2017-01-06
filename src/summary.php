<?php
date_default_timezone_set('PRC');
//echo "in summary.php <br>";
$query      = $_GET['query'];
$field		= $_GET['field'];
$sort		= $_GET['sort'];
$page       = isset($_GET['page'])?intval($_GET['page']):1;
$qf			= "";
$defType 	= "";
$mm			= "0.8";
$start		= ($page - 1) * 20;
$row		= 30;
$fq			= "";


$starttime = strtotime("now") - 86400 * 3; //三天以内的帖子
ini_set('display_errors',1);            //错误信息
ini_set('display_startup_errors',1);    //php启动错误信息
error_reporting(-1);                    //打印出所有的 错误信息
ini_set('error_log', dirname(__FILE__) . '/error_log.txt'); //将出错信息输出到一个文本文件


//echo "query:$query\tfield:$field\tsort:$sort<br>";

if($field == "text") {
	$field = "";
	if(strpos($query, ":") === false) {
		$defType = "&defType=dismax";
	}
	$qf = urlencode("title^4 content^1 r_summs^0.5");
}
else {
	$field = $field.":";
}
$q = urlencode($field.$query);
if($sort == "rank") {
	$sort = "";	
}
else if($sort == "me") {
	$sort = urlencode("pvnum desc");
	$fq = urlencode("pdate:[$starttime TO *]");
}
else {
	$sort = urlencode($sort." desc");
}
$solr_url = "http://112.74.45.38:8983/solr/hupu/select?indent=on&q=$q&sort=$sort&qf=$qf&wt=json&start=$start&hl=on&hl.fl=title&rows=$row$defType&fq=$fq";
$sug_url = "http://112.74.45.38:8000/?query=".$q;
//echo $solr_url;

$contents = file_get_contents($solr_url);
$json_contents = json_decode($contents, true);
$total_page = intval($json_contents["response"]["numFound"] / 10);
if($total_page > 32) {
	$total_page = 32;
}

//sug
$sug_content = file_get_contents($sug_url);

echo json_encode(array(
  'data'=>$json_contents["response"]["docs"],
  'sug'=>trim($sug_content),
  'total_page'=>$total_page,
));
