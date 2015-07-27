<?php

Class Html {
    public function __construct() {
        $this->indent = 0;
        $this->fun = array();
        $this->txt = '';
    }

    public function __call ($tag, $arg) {
        if (!array_key_exists($tag, $this->fun)) {
            $this->fun[$tag] = function($tag, $arg) {
                #$this->txt .= $tag.PHP_EOL;
                return $tag;
            };
        }
        $indent = str_repeat(' ', $this->indent);
        $this->txt .= $indent.'<'.$tag.'>'.PHP_EOL;
        $this->indent += 1;
        $result = $this->fun[$tag]($tag, $arg);
        $this->indent -= 1;
        $this->txt .= $indent.'</'.$tag.'>'.PHP_EOL;
        return $result;
    }

    public function text() {
        return $this->txt;
    }
}

$H = new Html();
$H->hello('A');
$H->ciao('B');
$H->hola('C');
$H->hello('D');
echo $H->text();


/*
class Html {
    private static $indent = 0;
    private static $text = '';

    public function __construct($tag) {
        $this->tag = $tag;
        #$this->tags = array(
            #'HTML' => function() {
            #};,
            #'BODY' => function() {
            #};);
    }

    public function open($att=array()) {
        $tab = str_repeat('  ', self::$indent);
        self::$indent += 1;
        # TODO use $att
        self::$text .= $tab."<$this->tag>".PHP_EOL;
    }

    public function shut() {
        self::$indent -= 1;
        $tab = str_repeat('  ', self::$indent);
        self::$text .= $tab."</$this->tag>".PHP_EOL;
    }

    public function text() {
        return self::$text;
    }
}

$TAGS = array('HTML', 'BODY', 'DIV');
$HTML = array();
foreach($TAGS as $tag) { $HTML[$tag] = new Html($tag); }

function wrap($tag, $fun, $arg=array(), $att=array()) {
    global $HTML;
    $force = true;
    try {
        $HTML[$tag]->open($att);
        $fun($arg);
        $force = false;
        $HTML[$tag]->shut();
    } catch (Exception $e) {
        echo "Exception on HTML[$tag]:".$e->getMessage().PHP_EOL;
        if ($force) {
            $HTML[$tag]->shut();
        }
        throw $e;
    }
}
 */

?>
