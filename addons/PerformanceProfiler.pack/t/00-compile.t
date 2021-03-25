use strict;
use warnings;

use Test::More;

use lib qw( lib extlib addons/PerformanceProfiler.pack/lib );

use_ok 'MT::Plugin::PerformanceProfiler';
use_ok 'MT::Plugin::PerformanceProfiler::KYTProfLogger';

done_testing;
