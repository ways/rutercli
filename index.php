<pre>
<?php
  $stopname='';
  $output=[];
  $return_var=0;
  $command='/local/www/graph.no/ruter/ruter.py';

  if (isset($_GET['stopname']) && ctype_alpha($_GET['stopname']) ) {
    $stopname=strtolower($_GET['stopname']);
    $command.=' '.$stopname;
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
  var_export(my_exec('echo -e $(</dev/stdin) | wc -l', 'h\\nel\\nlo')); 
  print_r(my_exec('/bin/ls'));
  print_r(my_exec($command));
?>

<form method="get" action="">
      <p>
         Stoppnavn: <input type="text" name="stopname">
         <input type="submit" value="Submit">
         </p>
      </form>
</pre>
