#!/usr/bin/env php
<?php
include_once('../Html.php');
function test() {
    global $HTML;
    $HTML['HTML']->open();
    $HTML['BODY']->open();
    $HTML['DIV']->open();
    $HTML['DIV']->shut();
    $HTML['BODY']->shut();
    $HTML['HTML']->shut();

    return $HTML['HTML']->text();
}

$hello = function ($arg) {
    $text = test().implode(' ', $arg).PHP_EOL;
};

$text = '<!DOCTYPE html>'.PHP_EOL;
.$HTML['HTML']->text();
$text = test()
wrap('HTML', $hello, array('hello', 'world'));
# $text .= implode(' ', $arg).PHP_EOL;
file_put_contents('../artifacts/php.Html.html', $text);
?>
