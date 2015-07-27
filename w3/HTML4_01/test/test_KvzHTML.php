#!/usr/bin/env php
<?php
error_reporting(E_ALL);
require_once '../KvzHTML.php';

// These are the default options, so might
// as well have initialized KvzHTML with an
// empty first argument
$H = new KvzHTML(array(
  'xhtml' => true,
  'track_toc' => false,
  'link_toc' => true,
  'indentation' => 4,
  'newlines' => true,
  'echo' => false,
  'buffer' => false,
  'xml' => false,
  'tidy' => false,
));

$tags = "html,head,title,body,h1,p,h2,table,th,tr,td";
foreach (explode(',', $tags) as $tag) {
    $TAG = strtoupper($tag);
    $evalMe = "function $TAG(\$a) { global \$H; return \$H->$tag(\$a); };";
    eval($evalMe);
}

$output = HTML(
  HEAD(
      TITLE('My page')
  ) .
  BODY(
      H1('Important website', array('bye'=>'ciao')) .
      P('Welcome to our website.') .
      H2('Users') .
      P('Here\'s a list of current users:') .
      TABLE(
          TR(TH('id') . TH('name') . TH('age')) .
          TR(TD('#1') . TD('Kevin van Zonneveld') . TD('26')) .
          TR(TD('#2') . TD('Foo Bar') . TD('28'))
      )
  )
);

echo $output;
?>
