<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="en">
<head>

  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0"> 

<pre>
<?php
  $stopname='';
  $output=[];
  $return_var=0;
  $command='/local/www/graph.no/ruter/ruter.py -a -n 3 ';

  if (isset($_GET['stopname']) && ctype_alpha($_GET['stopname']) ) {
    $stopname=strtolower($_GET['stopname']);
    $command.=$stopname;
  }

  echo "<h1>#</h1>";
  #echo exec ( $command, $output, $return_var );
  #echo shell_exec($command);
  #echo system ( $command);

  function my_exec($cmd, $input='')
         {$proc=proc_open($cmd, array(0=>array('pipe', 'r'), 1=>array('pipe', 'w'), 2=>array('pipe', 'w')), $pipes);
          fwrite($pipes[0], $input);fclose($pipes[0]);
          $stdout=stream_get_contents($pipes[1]);fclose($pipes[1]);
          $stderr=stream_get_contents($pipes[2]);fclose($pipes[2]);
          $rtn=proc_close($proc);
          return array('stdout'=>$stdout,
                       'stderr'=>$stderr,
                       'return'=>$rtn
                      );
         }
  #var_export(my_exec('echo -e $(</dev/stdin) | wc -l', 'h\\nel\\nlo')); 
  #print_r(my_exec($command));
  foreach (my_exec($command) as $line)
    echo $line;
?>

<form method="get" action="">
      <p>
         Stoppnavn: <input type="text" name="stopname">
         <input type="submit" value="Submit">
         </p>
      </form>
</pre>
